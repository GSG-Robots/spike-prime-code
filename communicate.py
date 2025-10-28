import asyncio
import contextlib
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
from collections import deque
from pathlib import Path
from typing import Iterator

import bleak
import bleak.backends.characteristic
import colorama
import mpy_cross
import watchdog.events
import watchdog.observers
import yaml
from tqdm import tqdm


class ForceReconnect(BaseException): ...


class RingIO:
    def __init__(self, initial_bytes=b""):
        self._buffer = bytearray(initial_bytes)

    def write(self, data: bytes):
        self._buffer.extend(data)

    def read(self, n: int):
        a = self._buffer[:n]
        self._buffer = self._buffer[n:]
        return bytes(a)


def clean_dir(dir: Path):
    for file in dir.glob("**"):
        if file == dir:
            continue
        if file.is_dir():
            clean_dir(file)
            os.rmdir(file)
        else:
            os.remove(file)


UART_SERVICE_UUID = "6E400001-B5A3-F393-E0A9-E50E24DCCA9E"
UART_TX_CHAR_UUID = "6E400002-B5A3-F393-E0A9-E50E24DCCA9E"
UART_RX_CHAR_UUID = "6E400003-B5A3-F393-E0A9-E50E24DCCA9E"


class BLEIOConnector:
    def __init__(self, device):
        self._ble = bleak.BleakClient(device, services=[UART_SERVICE_UUID], use_cached_services=True)
        self._packet = b""
        self._packet_handlers = {}
        self._error_handler = self._async_print
        self._pending_packets = deque()

    async def connect(self):
        await self._ble.connect()
        await self._ble.start_notify(UART_RX_CHAR_UUID.lower(), self._handle_rx)

    async def _async_print(self, data: bytes):
        print("Invalid Packet", data)

    def get_packet(self):
        if self._pending_packets:
            return self._pending_packets.popleft()
        return None

    async def _handle_rx(self, _: bleak.backends.characteristic.BleakGATTCharacteristic, data: bytearray):
        self._packet += data
        if b"\x1a" in self._packet:
            if len(self._packet) > 1:
                packet = self._packet[: self._packet.index(b"\x1a")]
                # print("<<", packet)
                packet_id = packet[:1]
                arguments = packet[1:]
                if packet_id == b"P":
                    print("|", arguments.decode(errors="replace"))
                elif packet_id == b"E":
                    print(
                        colorama.Fore.YELLOW + arguments.decode(errors="replace") + colorama.Fore.RESET,
                        file=sys.stderr,
                    )
                elif packet_id == b"!":
                    print(
                        colorama.Fore.RED + arguments.decode(errors="replace") + colorama.Fore.RESET,
                        file=sys.stderr,
                    )
                else:
                    self._pending_packets.append((packet_id, arguments))
            self._packet = b""

    async def send_packet(self, packet_id: int | bytes, data: bytes | None = None):
        if isinstance(packet_id, int):
            packet_id = packet_id.to_bytes()
        if data is None:
            data = b""
        # print(">>", packet_id + data)
        await self._ble.write_gatt_char(UART_TX_CHAR_UUID.lower(), packet_id + data + b"\x1a")


SRC_DIR = Path("src").absolute()
BUILD_DIR = Path("build").absolute()
mpy_cross.set_version("1.20", 6)


async def get_device():
    print("> Searching for devices...")
    ble_devices = await bleak.BleakScanner.discover(10)
    consider = [device for device in ble_devices if device.name is not None and device.name.startswith("GSG")]
    if len(consider) == 0:
        raise RuntimeError(f"No devices found: {', '.join(device.name or '?' for device in ble_devices)}")
    if len(consider) == 1:
        print("Only one device found")
        device = consider[0]
    else:
        print("Multiple devices foung:")
        for idx, device in enumerate(consider):
            print(f"  {idx + 1}. {device.name}")
        device_idx = int(input("Device: ")) - 1
        device = consider[device_idx]
    print(f"Connecting to {device.name}...")
    ble = BLEIOConnector(device)
    await ble.connect()
    return ble


def handle_error(error):
    print(error, file=sys.stderr)
    sys.exit(1)


async def expect_OK(BLEIO: BLEIOConnector, ignore=b"="):
    while True:
        await asyncio.sleep(0.001)
        packet = BLEIO.get_packet()
        if not packet:
            continue
        nxt, _ = packet
        if nxt in ignore:
            continue
        if nxt != b"K":
            print(f"Expecting OK, Invalid response {nxt}, resetting connection")
            await BLEIO.send_packet(b"$")
            raise ForceReconnect
        return True


async def send_file(BLEIO: BLEIOConnector, file, cb=None):
    while True:
        await asyncio.sleep(0.001)
        chunk = file.read(100)
        if not chunk:
            break
        await BLEIO.send_packet(b"C", chunk)
        await expect_OK(BLEIO)
        if cb is not None:
            cb(len(chunk))
    await BLEIO.send_packet(b"E")


def build_py(src: Path, dest: Path):
    result = subprocess.run(
        ["mpy-cross", src, "-o", dest],
        check=False,
        stderr=subprocess.PIPE,
    )
    if result.returncode != 0:
        print(result.stderr.decode("utf-8"))
        return False
    return True


def copy_py(src: Path, dest: Path):
    shutil.copy(src, dest)
    return True


def build_yaml(src: Path, dest: Path):
    with src.open() as f:
        data = yaml.safe_load(f)
    dest.write_text(json.dumps(data))
    return True


file_builders = {".py": (copy_py, ".py"), ".yaml": (build_yaml, ".json")}


def build(files: Iterator[Path]):
    for file in files:
        if file.is_dir():
            if file == SRC_DIR:
                continue
            folder = BUILD_DIR / file.relative_to(SRC_DIR)
            if file.exists():
                os.makedirs(folder, exist_ok=True)
            else:
                clean_dir(folder)
                os.rmdir(folder)
            continue
        # Skip stup files
        if file.suffix == ".pyi":
            continue
        builder, new_suffix = file_builders.get(file.suffix, (None, None))
        if not builder:
            print(f"Unable to build {file.suffix} file.")
            continue
        wanted_dest = BUILD_DIR / file.with_suffix(new_suffix).relative_to(SRC_DIR)

        if not file.exists():
            os.remove(wanted_dest)
            continue

        result = builder(file, wanted_dest)
        if not result:
            print(f"Failed to build {file.relative_to(SRC_DIR).as_posix()}.")
            continue


async def sync_path(BLEIO: BLEIOConnector, file: Path):
    path = file.relative_to(BUILD_DIR).as_posix()
    if path == ".":
        return None

    if not file.exists():
        await BLEIO.send_packet(b"R", ("/" + path).encode())
    elif file.is_dir():
        await BLEIO.send_packet(b"D", ("/" + path).encode())
        await expect_OK(BLEIO)
    else:
        hashv = hashlib.sha256(file.read_bytes()).hexdigest()
        await BLEIO.send_packet(b"F", ("/" + path + " " + hashv).encode())
        while True:
            await asyncio.sleep(0.001)
            packet = BLEIO.get_packet()
            if packet is None:
                continue
            nxt, _ = packet
            if nxt == b"=":
                continue
            if nxt == b"K":
                break
            if nxt != b"U":
                print(f"Expecting OK or U, Invalid response {nxt}, resetting connection")
                await BLEIO.send_packet(b"$")
                raise ForceReconnect
            with tqdm(
                total=file.stat().st_size,
                unit="B",
                unit_scale=True,
                desc=f"Uploading {file.name}",
            ) as bar:

                def tqdmcb(size: int):
                    bar.update(size)

                with file.open("rb") as f:
                    await send_file(BLEIO, f, tqdmcb)
    return False


async def sync_build_files(BLEIO):
    await BLEIO.send_packet(b"Y")
    await expect_OK(BLEIO)

    for file in BUILD_DIR.glob("**"):
        await sync_path(BLEIO, file)

    await BLEIO.send_packet(b"N")
    await expect_OK(BLEIO)


class FileUploader(watchdog.events.FileSystemEventHandler):
    modified = []
    _lock = False

    @contextlib.contextmanager
    def lock(self):
        while self._lock:
            time.sleep(0.1)
        self._lock = True
        yield
        self._lock = False

    def on_created(self, event: watchdog.events.DirCreatedEvent | watchdog.events.FileCreatedEvent):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_deleted(self, event: watchdog.events.DirDeletedEvent | watchdog.events.FileDeletedEvent):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_moved(self, event: watchdog.events.DirMovedEvent | watchdog.events.FileMovedEvent):
        with self.lock():
            self.modified.append(Path(event.src_path))


class FileBuilder(watchdog.events.FileSystemEventHandler):
    backlog = []
    _lock = False

    @contextlib.contextmanager
    def lock(self):
        while self._lock:
            time.sleep(0.1)
        self._lock = True
        yield
        self._lock = False

    def on_created(self, event: watchdog.events.DirCreatedEvent | watchdog.events.FileCreatedEvent):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_deleted(self, event: watchdog.events.DirDeletedEvent | watchdog.events.FileDeletedEvent):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_moved(self, event: watchdog.events.DirMovedEvent | watchdog.events.FileMovedEvent):
        with self.lock():
            self.backlog.append(Path(event.src_path))
            self.backlog.append(Path(event.dest_path))


async def sync_stream(BLEIO: BLEIOConnector, timeout=10):
    otm = time.time()
    otm_packet = str(otm).encode()
    await BLEIO.send_packet(b"=", otm_packet)
    while time.time() < otm + timeout:
        await asyncio.sleep(0.001)
        resp = BLEIO.get_packet()
        # print(22, resp)
        if resp is None:
            await BLEIO.send_packet(b"=", otm_packet)
            await asyncio.sleep(1)
            continue
        nxt, tm = resp
        if nxt == b"=" and tm == otm_packet:
            return
    raise TimeoutError(f"Hub failed to sync after {timeout} seconds.")


async def main():
    BLEIO = await get_device()
    # time.sleep(1)
    await sync_stream(BLEIO)
    print("Connected to device.")
    print("Preparing environment...")
    if not SRC_DIR.exists():
        os.makedirs(SRC_DIR)
    if not BUILD_DIR.exists():
        os.makedirs(BUILD_DIR)
    clean_dir(BUILD_DIR)

    print("Building...")
    build(SRC_DIR.glob("**"))
    print("Initial file synchronization...")
    await sync_build_files(BLEIO)
    print("Restarting program...")
    await BLEIO.send_packet(b"P")
    await expect_OK(BLEIO)

    observer = watchdog.observers.Observer()
    file_builder = FileBuilder()
    file_uploader = FileUploader()
    observer.schedule(file_builder, SRC_DIR, recursive=True)
    observer.schedule(file_uploader, BUILD_DIR, recursive=True)
    observer.start()
    blocked = False
    try:
        while True:
            await asyncio.sleep(0.01)
            if not BLEIO._ble.is_connected:
                raise ConnectionAbortedError
            packet = BLEIO.get_packet()
            if packet is not None:
                nxt, args = packet
                print("Unexpected Packet")
            with file_builder.lock():
                if len(file_builder.backlog) > 0:
                    print("Rebuilding...")
                    unique = []
                    for task in file_builder.backlog:
                        if task in unique:
                            continue
                        unique.append(task)
                        await asyncio.sleep(0.001)

                    build(unique)
                    file_builder.backlog = []

                    print("Build done.")
            with file_uploader.lock():
                if file_uploader.modified:
                    if blocked:
                        continue
                    print("> Updating...")
                    done = []
                    while file_uploader.modified:
                        task = file_uploader.modified.pop()
                        if task in done:
                            continue
                        done.append(task)
                        undermined = await sync_path(BLEIO, task)
                        if undermined:
                            file_uploader.modified.append(task)
                            break
                        await asyncio.sleep(0.001)
                    else:
                        print("> Restarting...")
                        if not file_uploader.modified:
                            await BLEIO.send_packet(b"P")
                            await expect_OK(BLEIO)

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


asyncio.run(main())

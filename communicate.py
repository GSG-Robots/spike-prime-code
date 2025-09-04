import asyncio
import binascii
import contextlib
import hashlib
import json
import os
from struct import pack
import subprocess
import sys
import time
import traceback
from pathlib import Path
from typing import Any, Callable, Coroutine, Iterator, overload

import bleak
import bleak.backends.characteristic
import colorama
import mpy_cross
import serial.tools.list_ports
import watchdog.events
import watchdog.observers
import yaml
from tqdm import tqdm

from .spielzeug.bleio import BLEIO


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
    async def __init__(self, device):
        self._ble = bleak.BleakClient(
            device, services=[UART_SERVICE_UUID], use_cached_services=True
        )
        self._packet = b""
        self._packet_handlers = {}
        self._error_handler = self._async_print
        await self._ble.connect()

    async def _async_print(self, data: bytes):
        print("Invalid Packet", data)

    async def _handle_packet(self, packet: bytes):
        packet_handler = self._packet_handlers.get(packet[0])
        if packet_handler is None:
            await self._error_handler(packet)
            return
        arguments = packet[1:]
        await packet_handler(arguments)

    async def handle_rx(
        self, _: bleak.backends.characteristic.BleakGATTCharacteristic, data: bytearray
    ):
        self._packet += data
        if b"\x1a" in data:
            if len(self._packet) > 1:
                await self._handle_packet(self._packet[: self._packet.index(b"\x1a")])
            self._packet = b""

    async def send_packet(self, packet_id: int | bytes, data: bytes | None = None):
        if isinstance(packet_id, int):
            packet_id = packet_id.to_bytes()
        if data is None:
            data = b""
        await self._ble.write_gatt_char(UART_TX_CHAR_UUID.lower(), packet_id + data)


SRC_DIR = Path("src").absolute()
BUILD_DIR = Path("build").absolute()
mpy_cross.set_version("1.20", 6)



async def get_device():
    print("> Searching for devices...")
    # ble_devices = devices = await bleak.BleakScanner.discover(10)
    # for device in ble_devices:
    #     if device.name != "GSG-Robots":
    #         continue
    device = "34:08:E1:8A:87:0D"
    return BLEIOConnector(device)

def handle_error(error):
    print(error, file=sys.stderr)
    sys.exit(1)


async def expect_OK():
    while True:
        await asyncio.sleep(0.001)
        nxt, _ = await get_next()
        if nxt in "BD":
            continue
        if nxt != "K":
            print(f"Expecting OK, Invalid response {nxt}, resetting connection")
            await write("$")
            raise ForceReconnect()
        return True


async def send_file(file, cb=None):
    while True:
        await asyncio.sleep(0.001)
        chunk = file.read(192)
        if not chunk:
            break
        await write("C", chunk)
        await expect_OK()
        if cb is not None:
            cb(len(chunk))
    await write("E")


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


def build_yaml(src: Path, dest: Path):
    with src.open() as f:
        data = yaml.safe_load(f)
    dest.write_text(json.dumps(data))
    return True


file_builders = {".py": (build_py, ".mpy"), ".yaml": (build_yaml, ".json")}


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
        return
    if not file.exists():
        await BLEIO.send_packet(b"R", ("/" + path).encode())
    if file.is_dir():
        await BLEIO.send_packet(b"D", ("/" + path).encode())
        await expect_OK()
    else:
        hashv = hashlib.sha256(file.read_bytes()).hexdigest()
        await BLEIO.send_packet(b"F", ("/" + path + " " + hashv).encode())
        while True:
            await asyncio.sleep(0.001)
            nxt, _ = await get_next()
            if nxt == "B":
                return True
            if nxt == "D":
                continue
            if nxt == "K":
                break
            elif nxt != "U":
                print(
                    f"Expecting OK or U, Invalid response {nxt}, resetting connection"
                )
                await write("$")
                raise ForceReconnect()
            with tqdm(
                total=file.stat().st_size,
                unit="B",
                unit_scale=True,
                desc=f"Uploading {file.name}",
            ) as bar:

                def tqdmcb(size: int):
                    bar.update(size)

                with file.open("rb") as f:
                    await send_file(f, tqdmcb)
                await expect_OK()
                break
    return False


async def sync_build_files():
    await write("Y")
    await expect_OK()

    for file in BUILD_DIR.glob("**"):
        await sync_path(file)

    await write("N")
    await expect_OK()


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

    def on_created(
        self, event: watchdog.events.DirCreatedEvent | watchdog.events.FileCreatedEvent
    ):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_deleted(
        self, event: watchdog.events.DirDeletedEvent | watchdog.events.FileDeletedEvent
    ):
        with self.lock():
            self.modified.append(Path(event.src_path))

    def on_moved(
        self, event: watchdog.events.DirMovedEvent | watchdog.events.FileMovedEvent
    ):
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

    def on_created(
        self, event: watchdog.events.DirCreatedEvent | watchdog.events.FileCreatedEvent
    ):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_deleted(
        self, event: watchdog.events.DirDeletedEvent | watchdog.events.FileDeletedEvent
    ):
        with self.lock():
            self.backlog.append(Path(event.src_path))

    def on_moved(
        self, event: watchdog.events.DirMovedEvent | watchdog.events.FileMovedEvent
    ):
        with self.lock():
            self.backlog.append(Path(event.src_path))
            self.backlog.append(Path(event.dest_path))


async def sync_stream(timeout=10):
    otm = time.time()
    await write("=", str(otm))
    while time.time() < otm + timeout:
        await asyncio.sleep(0.001)
        resp = await get_next(10, ignore_errors=True, exclude_sync=False)
        if resp is None:
            await write("=", str(otm))
            await asyncio.sleep(1)
            continue
        nxt, tm = resp
        if nxt == "=" and tm == str(otm):
            return
    raise TimeoutError(f"Hub failed to sync after {timeout} seconds.")


async def main():
    global SERIAL, BT_IOS
    ser = await get_device()
    if ser is None:
        return
    SERIAL, BT_IOS = ser
    # time.sleep(1)
    await sync_stream()
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
    await sync_build_files()
    print("Restarting program...")
    await write("P")
    await expect_OK()

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
            if SERIAL is not None and SERIAL.closed:
                raise ConnectionAbortedError
            if (
                SERIAL is not None
                and SERIAL.in_waiting
                or BT_IOS is not None
                and BT_IOS.in_waiting
            ):
                cmd = await get_next(1)
                if cmd is not None:
                    nxt, args = cmd
                    if nxt == "B":
                        blocked = True
                    elif nxt == "D":
                        blocked = False
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
                        undermined = await sync_path(task)
                        if undermined:
                            file_uploader.modified.append(task)
                            break
                        await asyncio.sleep(0.001)
                    else:
                        print("> Restarting...")
                        if not file_uploader.modified:
                            await write("P")
                            await expect_OK()

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


asyncio.run(main())

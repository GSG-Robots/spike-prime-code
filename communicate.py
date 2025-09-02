import asyncio
import binascii
import contextlib
import hashlib
import json
import os
import subprocess
import sys
import time
from pathlib import Path
import traceback
from typing import Any, Callable, Coroutine, Iterator, overload

import bleak.backends
import bleak.backends.characteristic
import colorama
import mpy_cross
from serial import Serial
import serial.tools.list_ports
import watchdog.events
import watchdog.observers
import yaml
from tqdm import tqdm
import bleak


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


class IOStore:
    def __init__(self):
        self.BTIN = RingIO()
        self.BTOUT = RingIO()
        self.in_waiting = 0
        self.out_waiting = 0
        self._in_lock = asyncio.Lock()
        self._out_lock = asyncio.Lock()

    async def read(self, length: int):
        while self.in_waiting < length:
            await asyncio.sleep(0.001)
        await self._in_lock.acquire()
        self.in_waiting -= length
        self._in_lock.release()
        return self.BTIN.read(length)

    async def write(self, data: bytes):
        self.BTOUT.write(data)
        await self._out_lock.acquire()
        self.out_waiting += len(data)
        self._out_lock.release()


debug = True
SRC_DIR = Path("src").absolute()
BUILD_DIR = Path("build").absolute()
SERIAL: Serial | None = None
BT_IOS: IOStore | None = None
mpy_cross.set_version("1.20", 6)


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


async def handle_bleio(address, ios: IOStore, finished_callback):
    async def handle_rx(
        _: bleak.backends.characteristic.BleakGATTCharacteristic, data: bytearray
    ):
        ios.BTIN.write(data)
        await ios._in_lock.acquire()
        ios.in_waiting += len(data)
        ios._in_lock.release()

    async with bleak.BleakClient(
        address, services=[UART_SERVICE_UUID], use_cached_services=True
    ) as client:
        print("Connected.")
        # paired = await client.pair()
        # if not paired:
        #     print("Failed to pair.")
        #     sys.exit(1)
        # print("Paired.")
        finished_callback()
        await client.start_notify(UART_RX_CHAR_UUID.lower(), handle_rx)
        while True:
            if ios.out_waiting:
                data = ios.BTOUT.read(min(ios.out_waiting, 60))
                await ios._out_lock.acquire()
                ios.out_waiting -= len(data)
                ios._out_lock.release()
                await client.write_gatt_char(UART_TX_CHAR_UUID.lower(), data)
                await asyncio.sleep(0.001)
                continue
            await asyncio.sleep(0.001)


async def get_device():
    print("> Searching for devices...")
    # ble_devices = devices = await bleak.BleakScanner.discover(10)
    # for device in ble_devices:
    #     if device.name != "GSG-Robots":
    #         continue
    device = "34:08:E1:8A:87:0D"
    ios = IOStore()
    finished = asyncio.Event()
    asyncio.create_task(handle_bleio(device, ios, finished.set))
    print(1)
    await finished.wait()
    print("Connection established")
    return None, ios
    devices = serial.tools.list_ports.comports()
    if len(devices) == 0:
        print("Error: No devices found")
        return
    if len(devices) == 1:
        device_choice = devices[0]
    else:
        for index, device in enumerate(devices):
            print(f"{index + 1:>2}. {device.device}")
        device_choice = devices[int(input("Device: ")) - 1]

    print(f"> Connecting to {device_choice}...")
    return serial.Serial(device_choice.device, 115200), None


def handle_error(error):
    print(error, file=sys.stderr)
    sys.exit(1)


async def _get_next(
    timeout=-1,
) -> tuple[str, str | None] | None:
    READ_FROM: list[Callable[[int], Coroutine[Any, Any, bytes]]] = []
    if SERIAL is not None and SERIAL.in_waiting:

        async def read(n: int) -> bytes:
            return SERIAL.read(n)

        READ_FROM.append(read)
    if BT_IOS is not None and BT_IOS.in_waiting:
        READ_FROM.append(BT_IOS.read)
    for read in READ_FROM:
        while (a := await read(1)) != b":":
            if debug:
                print(a.decode(), end="")
        if debug:
            print()

        cmd = (await read(1)).decode()
        nxt = await read(1)
        if nxt == b"]":
            return cmd, None
        else:
            lns = nxt + await read(3)
            try:
                ln = int(lns)
            except ValueError:
                print(f"Failed {lns} {cmd}")
                ln = 0
            arg = await read(ln)
            try:
                decoded_arg = binascii.a2b_base64(arg).decode()
            except Exception as e:
                traceback.print_exception(e)
                print("Failed to handle packet, resetting connection")
                write("$")
                raise ForceReconnect()
            return cmd, decoded_arg
    return None


async def write(cmd, args=None):
    if debug:
        print("write", cmd, args)
    msg = b":" + cmd.encode()
    if args is not None:
        if not isinstance(args, bytes):
            args = args.encode()
        encoded_args = binascii.b2a_base64(args, newline=False)
        msg += ("0000" + str(len(encoded_args)))[-4:].encode() + encoded_args
    else:
        msg += b"]"
    if SERIAL is not None:
        SERIAL.write(msg)
    if BT_IOS is not None:
        await BT_IOS.write(msg)


@overload
async def get_next(
    max_retries: int, /, *, ignore_errors: bool = False, exclude_sync: bool = True
) -> tuple[str, str | None] | None: ...
@overload
async def get_next(*, ignore_errors: bool = False, exclude_sync: bool = True) -> tuple[str, str | None]: ...


async def get_next(max_retries=None, /, *, ignore_errors=False, exclude_sync=True):
    retries = 0
    while True:
        await asyncio.sleep(0.001)
        result = await _get_next(0)
        if not result:
            if max_retries:
                retries += 1
                if retries >= max_retries:
                    return None
            continue
        if debug:
            print("read", *result)
        if result[0] == "!" and not ignore_errors:
            handle_error(result[1])
            return result
        elif result[0] == "P":
            assert result[1]
            args, kwargs = json.loads(result[1])
            kwargs["file"] = None
            print("|", *args, **kwargs)
        elif result[0] == "E":
            assert result[1]
            print(colorama.Fore.RED + result[1] + colorama.Fore.RESET, file=sys.stderr)
        elif exclude_sync and result[0] == "=":
            continue
        else:
            return result


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


async def sync_path(file: Path):
    path = file.relative_to(BUILD_DIR).as_posix()
    if path == ".":
        return
    if not file.exists():
        await write("R", "/" + path)
    if file.is_dir():
        await write("D", "/" + path)
        await expect_OK()
    else:
        hashv = hashlib.sha256(file.read_bytes()).hexdigest()
        await write("F", "/" + path + " " + hashv)
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

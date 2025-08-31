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
from typing import Iterator, overload

import colorama
import mpy_cross
from serial import Serial
import serial.tools.list_ports
import watchdog.events
import watchdog.observers
import yaml
from tqdm import tqdm


class ForceReconnect(BaseException): ...


debug = False
SRC_DIR = Path("src").absolute()
BUILD_DIR = Path("build").absolute()
SERIAL: Serial | None = None
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


def get_device():
    print("> Searching for devices...")
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
    return serial.Serial(device_choice.device, 115200)


def handle_error(error):
    print(error, file=sys.stderr)
    sys.exit(1)


def _get_next(
    timeout=-1,
) -> tuple[str, str | None] | None:
    assert SERIAL is not None
    if SERIAL.in_waiting:
        while (a := SERIAL.read(1)) != b":":
            if debug:
                print(a.decode(), end="")
        if debug:
            print()

        cmd = SERIAL.read(1).decode()
        nxt = SERIAL.read(1)
        if nxt == b"]":
            return cmd, None
        else:
            lns = nxt + SERIAL.read(3)
            try:
                ln = int(lns)
            except ValueError:
                print(f"Failed {lns} {cmd}")
                ln = 0
            arg = SERIAL.read(ln)
            try:
                decoded_arg = binascii.a2b_base64(arg).decode()
            except Exception as e:
                traceback.print_exception(e)
                print("Failed to handle packet, resetting connection")
                write("$")
                raise ForceReconnect()
            return cmd, decoded_arg
    return None




def write(cmd, args=None):
    if debug:
        print("write", cmd, args)
    assert SERIAL is not None
    SERIAL.write(b":" + cmd.encode())
    if args is not None:
        if not isinstance(args, bytes):
            args = args.encode()
        encoded_args = binascii.b2a_base64(args, newline=False)
        SERIAL.write(("0000" + str(len(encoded_args)))[-4:].encode())
        SERIAL.write(encoded_args)
    else:
        SERIAL.write(b"]")


@overload
async def get_next(
    max_retries: int, /, *, ignore_errors: bool = False
) -> tuple[str, str | None] | None: ...
@overload
async def get_next(*, ignore_errors: bool = False) -> tuple[str, str | None]: ...


async def get_next(max_retries=None, /, *,ignore_errors=False):
    retries = 0
    while True:
        result = _get_next(0)
        if not result:
            await asyncio.sleep(0.1)
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
        else:
            return result


async def expect_OK():
    while True:
        nxt, _ = await get_next()
        if nxt in "BD":
            continue
        if nxt != "K":
            print(f"Expecting OK, Invalid response {nxt}, resetting connection")
            write("$")
            raise ForceReconnect()
        return True


async def send_file(file, cb=None):
    while True:
        chunk = file.read(192)
        if not chunk:
            break
        write("C", chunk)
        await expect_OK()
        if cb is not None:
            cb()
    write("E")


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
        write("R", "/" + path)
    if file.is_dir():
        write("D", "/" + path)
        await expect_OK()
    else:
        hashv = hashlib.sha256(file.read_bytes()).hexdigest()
        write("F", "/" + path + " " + hashv)
        while True:
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
                write("$")
                raise ForceReconnect()
            with tqdm(
                total=file.stat().st_size,
                unit="B",
                unit_scale=True,
                desc=f"Uploading {file.name}",
            ) as bar:

                def tqdmcb():
                    bar.update(192)

                with file.open("rb") as f:
                    await send_file(f, tqdmcb)
                await expect_OK()
                break
    return False


async def sync_build_files():
    write("Y")
    await expect_OK()

    for file in BUILD_DIR.glob("**"):
        await sync_path(file)

    write("N")
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
    write("=", str(otm))
    while time.time() < otm + timeout:
        resp = await get_next(10, ignore_errors=True)
        if resp is None:
            write("=", str(otm))
            continue
        nxt, tm = resp
        if nxt == "=" and tm == str(otm):
            return
    raise TimeoutError(f"Hub failed to sync after {timeout} seconds.")


async def main():
    global SERIAL
    ser = get_device()
    SERIAL = ser
    time.sleep(1)
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
    write("P")
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
            time.sleep(0.1)
            if ser.closed:
                raise ConnectionAbortedError
            if ser.in_waiting:
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

                    build(unique)
                    file_builder.backlog = []

                    print("Build done.")
            with file_uploader.lock():
                if len(file_uploader.modified) > 0:
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
                    else:
                        print("> Restarting...")
                        write("P")
                        await expect_OK()

    except KeyboardInterrupt:
        observer.stop()
    observer.join()


asyncio.run(main())

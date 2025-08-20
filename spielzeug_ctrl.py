import contextlib
import hashlib
import json
import os
import subprocess
import time
from pathlib import Path
from typing import Iterator

import serial.tools.list_ports
import serial.tools.list_ports_windows
import watchdog.events
import watchdog.observers
import yaml
from tqdm import tqdm

from spielzeug import spielzeug_lib

print("Preparing environment...")
src_dir = Path("src").absolute()
build_dir = Path("build").absolute()

if not src_dir.exists():
    os.makedirs(src_dir)
if not build_dir.exists():
    os.makedirs(build_dir)


def clean_dir(dir: Path):
    for file in dir.glob("**"):
        if file == dir:
            continue
        if file.is_dir():
            clean_dir(file)
            os.rmdir(file)
        else:
            os.remove(file)


clean_dir(build_dir)


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
            print(f"{index+1:>2}. {device.device}")
        device_choice = devices[int(input("Device: ")) - 1]

    print(f"> Connecting to {device_choice}...")
    return serial.Serial(device_choice.device, 115200)


def build_py(src: Path, dest: Path):
    result = subprocess.run(
        ["mpy-cross-v5", src, "-o", dest],
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
            if file == src_dir:
                continue
            folder = build_dir / file.relative_to(src_dir)
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
        wanted_dest = build_dir / file.with_suffix(new_suffix).relative_to(src_dir)

        if not file.exists():
            os.remove(wanted_dest)
            continue

        result = builder(file, wanted_dest)
        if not result:
            print(f"Failed to build {file.relative_to(src_dir).as_posix()}.")
            continue


def list_build_files():
    files = []
    for file in build_dir.glob("**"):
        path = file.relative_to(build_dir).as_posix()
        if file.is_dir():
            if path != ".":
                yield "dir", path, file
        else:
            hashv = hashlib.sha256(file.read_bytes()).hexdigest()
            yield "file", path, hashv, file
    return files


def sync_build_files():
    spielzeug_lib.send_command("sync-down")
    spielzeug_lib.wait_for_keyword("ready")

    for entry in list_build_files():
        spielzeug_lib.send_command(*entry[:-1])
        if entry[0] == "dir":
            spielzeug_lib.wait_for_keyword("done")
            continue
        command, arguments = spielzeug_lib.get_command()
        if command == "done":
            continue
        elif command == "update":
            with tqdm(
                total=entry[-1].stat().st_size,
                unit="B",
                unit_scale=True,
                desc=f"Uploading {entry[-1].name}",
            ) as bar:

                def tqdmcb():
                    bar.update(192)

                with entry[-1].open("rb") as f:
                    spielzeug_lib.send_raw_data(f, tqdmcb)
            spielzeug_lib.wait_for_keyword("done")
        else:
            print("Unexpected command while syncing file", command, arguments)

    spielzeug_lib.send_command("done")
    spielzeug_lib.wait_for_keyword("DONE")


class FileUploader(watchdog.events.FileSystemEventHandler):
    tasks = []
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
            if event.is_directory:
                self.tasks.append(("mkdir", Path(event.src_path)))
            else:
                self.tasks.append(("write", Path(event.src_path)))

    def on_modified(
        self,
        event: watchdog.events.DirModifiedEvent | watchdog.events.FileModifiedEvent,
    ):
        with self.lock():
            if event.is_directory:
                return
            self.tasks.append(("write", Path(event.src_path)))

    def on_deleted(
        self, event: watchdog.events.DirDeletedEvent | watchdog.events.FileDeletedEvent
    ):
        with self.lock():
            if event.is_directory:
                self.tasks.append(("rmdir", Path(event.src_path)))
            else:
                self.tasks.append(("rm", Path(event.src_path)))

    def on_moved(
        self, event: watchdog.events.DirMovedEvent | watchdog.events.FileMovedEvent
    ):
        with self.lock():
            if event.is_directory:
                self.tasks.append(("mvdir", Path(event.src_path)))
            else:
                self.tasks.append(("mv", Path(event.src_path)))


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


def main():
    print("Building...")
    build(src_dir.glob("**"))
    ser = get_device()
    time.sleep(1)
    spielzeug_lib.set_ser(ser, 5)
    spielzeug_lib.send_command("cancel-any")
    print("Connected to device.")
    print("Initial file synchronization...")
    sync_build_files()
    print("Restarting program...")
    spielzeug_lib.send_command("start")
    try:
        spielzeug_lib.wait_for_keyword("DONE")
    except RuntimeError as e:
        print("--- REMOTE ERROR ---")
        print(e)

    print()
    print("> IDLE", end="\r")

    observer = watchdog.observers.Observer()
    file_builder = FileBuilder()
    file_uploader = FileUploader()
    observer.schedule(file_builder, src_dir, recursive=True)
    observer.schedule(file_uploader, build_dir, recursive=True)
    observer.start()
    blocked = False
    try:
        while True:
            time.sleep(0.1)
            if ser.closed:
                raise ConnectionAbortedError
            if ser.in_waiting:
                line = ser.readline().strip()
                if line == b"blocked":
                    blocked = True
                elif line == b"unblocked":
                    blocked = False
                else:
                    print("O:", line.decode("utf-8"))
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
                if len(file_uploader.tasks) > 0:
                    if blocked:
                        continue
                    print("> Updating...")
                    done = []
                    for task in file_uploader.tasks:
                        if task in done:
                            continue
                        done.append(task)
                        spielzeug_lib.send_command(
                            task[0],
                            task[1].relative_to(build_dir).as_posix(),
                        )
                        if task[0] == "write":
                            with task[1].open("rb") as f:
                                spielzeug_lib.send_raw_data(f)
                        spielzeug_lib.wait_for_keyword("DONE")
                    print("> Restarting...")
                    spielzeug_lib.send_command("start")
                    try:
                        spielzeug_lib.wait_for_keyword("DONE")
                    except RuntimeError as e:
                        print("--- REMOTE ERROR ---")
                        print(e)
                        print()
                        print("> IDLE")
                    else:
                        print("> IDLE")
                    file_uploader.tasks = []
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


main()

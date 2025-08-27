import binascii
import hashlib
import io
import os
import sys
import spielzeug_lib
import hub
import uasyncio as asyncio
import time


class Interface:
    def read(*args, **kwargs):
        return sys.stdin.read(*args, **kwargs)

    def readline(self, *args, **kwargs):
        return input(*args, **kwargs).encode()

    def write(self, *args, **kwargs):
        print(*[a.decode() for a in args], **kwargs, end="")


usb = Interface()
spielzeug_lib.set_ser(usb, 5)
spielzeug_lib.send_command("START")


# @hub.button.connect.callback
# def button_callback(i):
#     hub.sound.beep(700, 100)
#     hub.bluetooth.discoverable(90000)


if "src" not in os.listdir("/flash"):
    os.mkdir("/flash/src")


def clean_tree(path=""):
    for item, type, *_ in os.ilistdir("/flash/src/" + path):
        item_path = "/flash/src/" + path + item
        if type == 0x8000:
            os.remove(item_path)
        elif type == 0x4000:
            clean_tree(path + item + "/")
            os.rmdir(item_path)


def list_files(path=""):
    files = []
    directories = []
    for item, type, *_ in os.ilistdir("/flash/src/" + path):
        item_path = path + item
        if type == 0x8000:
            files.append(item_path)
        elif type == 0x4000:
            directories.append(item_path)
            f, d = list_files(item_path + "/")
            files.extend(f)
            directories.extend(d)
    return files, directories


def perform_sync():
    old_files, old_directories = list_files()
    spielzeug_lib.send_command("ready", ",".join(old_files + old_directories))

    while True:
        command, arguments = spielzeug_lib.get_command()
        if command is None:
            continue

        if command == "done":
            break
        elif command == "file":
            path, hash = arguments.rsplit(" ", 1)
            if path in old_files:
                old_files.remove(path)

                with open("/flash/src/" + path, "rb") as f:
                    old_hash = binascii.hexlify(
                        hashlib.sha256(f.read()).digest()
                    ).decode()

                if old_hash == hash:
                    spielzeug_lib.send_command("done")
                    continue
            spielzeug_lib.send_command("update")
            data = spielzeug_lib.intake_raw_data()
            with open("/flash/src/" + path, "wb") as f:
                f.write(data)
            spielzeug_lib.send_command("done")
        elif command == "dir":
            if arguments in old_directories:
                old_directories.remove(arguments)
            else:
                os.mkdir("/flash/src/" + arguments)
            spielzeug_lib.send_command("done")

    for file in old_files:
        os.remove("/flash/src/" + file)

    for directory in reversed(old_directories):
        os.rmdir("/flash/src/" + directory)


prog_task = None
has_stopped = asyncio.Event()


async def task_wrapper(coro):
    has_stopped.clear()
    try:
        await coro
    finally:
        has_stopped.set()
        
async def start_main():
    ...
    # global prog_task
    # if prog_task:
    #     prog_task.cancel()
    #     await has_stopped.wait()
    # for module in sys.modules.keys():
    #     if module == "src" or module.startswith("src."):
    #         del sys.modules[module]
    # hub.display.clear()
    # module = __import__("src")
    # prog_task = asyncio.create_task(task_wrapper(module.loop()))
import color

async def main_loop():
    hub.light_matrix.show(
        [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 100, 0, 100, 0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
    )
    await asyncio.sleep_ms(2000)
    hub.light_matrix.clear()
    try:
        await start_main()
    except Exception as e:
        print("show_error", binascii.b2a_base64(str(e).encode()).decode())
        hub.light.color(hub.light.POWER, color.RED)
        time.sleep(0.1)
        hub.light.color(hub.light.POWER, color.BLACK)
        time.sleep(0.1)
        hub.light.color(hub.light.POWER, color.RED)
    while spielzeug_lib.ser:
        try:
            command, arguments = spielzeug_lib.get_command()
            if command is None:
                await asyncio.sleep_ms(100)
                continue
            hub.light_matrix.show([100]*25)
            if command == "clean":
                clean_tree()
                spielzeug_lib.send_command("DONE")
            elif command == "sync-down":
                perform_sync()
                spielzeug_lib.send_command("DONE")
            elif command == "start":
                await start_main()
                spielzeug_lib.send_command("DONE")
            elif command == "stop":
                if prog_task:
                    prog_task.cancel()
                    await has_stopped.wait()
                spielzeug_lib.send_command("DONE")
            elif command == "write":
                data = spielzeug_lib.intake_raw_data()
                with open("/flash/src/" + arguments, "wb") as f:
                    f.write(data)
                spielzeug_lib.send_command("DONE")
            elif command == "rm":
                os.remove("/flash/src/" + arguments)
            elif command == "rmdir":
                os.rmdir("/flash/src/" + arguments)
            elif command == "mkdir":
                os.mkdir("/flash/src/" + arguments)
                spielzeug_lib.send_command("DONE")
            elif command == "read":
                with open("/flash/src/" + arguments, "rb") as f:
                    spielzeug_lib.send_raw_data(f)
            else:
                print(
                    "error",
                    binascii.b2a_base64(
                        "GOT unknown command '" + str(command) + "'"
                    ).decode(),
                )
        except KeyboardInterrupt:
            await asyncio.sleep_ms(100)
            continue
        except Exception as e:
            buf = io.StringIO()
            sys.print_exception(e, buf)
            print("error", binascii.b2a_base64(buf.getvalue()).decode())
        await asyncio.sleep_ms(100)

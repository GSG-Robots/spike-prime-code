import binascii
import hashlib
import io
import os
import sys
import spielzeug_lib
import hub
import uasyncio as asyncio


usb = hub.USB_VCP()
spielzeug_lib.set_ser(usb, 5)


if "spielzeugs" not in os.listdir("/"):
    os.mkdir("/spielzeugs")


async def display_connected():
    connected = False
    while True:
        if usb.isconnected():
            if not connected:
                spielzeug_lib.send_command("START")
                connected = True
                hub.led(3)
        elif connected:
            connected = False
            hub.led(0)
        await asyncio.sleep_ms(50)


def clean_tree(path=""):
    for item, type, *_ in os.ilistdir("/spielzeugs/" + path):
        item_path = "/spielzeugs/" + path + item
        if type == 0x8000:
            os.remove(item_path)
        elif type == 0x4000:
            clean_tree(path + item + "/")
            os.rmdir(item_path)


def list_files(path=""):
    files = []
    directories = []
    for item, type, *_ in os.ilistdir("/spielzeugs/" + path):
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

                with open("/spielzeugs/" + path, "rb") as f:
                    old_hash = binascii.hexlify(
                        hashlib.sha256(f.read()).digest()
                    ).decode()

                if old_hash == hash:
                    spielzeug_lib.send_command("done")
                    continue
            spielzeug_lib.send_command("update")
            data = spielzeug_lib.intake_raw_data()
            with open("/spielzeugs/" + path, "wb") as f:
                f.write(data)
            spielzeug_lib.send_command("done")
        elif command == "dir":
            if arguments in old_directories:
                old_directories.remove(arguments)
            else:
                os.mkdir("/spielzeugs/" + arguments)
            spielzeug_lib.send_command("done")

    for file in old_files:
        os.remove("/spielzeugs/" + file)

    for directory in reversed(old_directories):
        os.rmdir("/spielzeugs/" + directory)


prog_task = None
has_stopped = asyncio.Event()


async def task_wrapper(coro):
    has_stopped.clear()
    try:
        await coro
    finally:
        has_stopped.set()


async def start_main():
    global prog_task
    if prog_task:
        prog_task.cancel()
        await has_stopped.wait()
    for module in sys.modules.keys():
        if module == "spielzeugs" or module.startswith("spielzeugs."):
            del sys.modules[module]
    hub.display.clear()
    module = __import__("spielzeugs")
    prog_task = asyncio.create_task(task_wrapper(module.loop()))


async def main_loop():
    asyncio.create_task(display_connected())
    hub.display.show(hub.Image("00000:00000:90909:00000:00000"))
    await asyncio.sleep_ms(2000)
    hub.display.clear()
    try:
        await start_main()
    except Exception as e:
        print("error", binascii.b2a_base64(str(e).encode()).decode())
    while True:
        if usb.isconnected():
            try:
                command, arguments = spielzeug_lib.get_command()
                if command is None:
                    await asyncio.sleep_ms(30)
                    continue
                hub.display.show(hub.Image("99999:99999:99999:99999:99999"))
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
                    with open("/spielzeugs/" + arguments, "wb") as f:
                        f.write(data)
                    spielzeug_lib.send_command("DONE")
                elif command == "rm":
                    os.remove("/spielzeugs/" + arguments)
                elif command == "rmdir":
                    os.remove("/spielzeugs/" + arguments)
                elif command == "mkdir":
                    os.mkdir("/spielzeugs/" + arguments)
                    spielzeug_lib.send_command("DONE")
                elif command == "read":
                    with open("/spielzeugs/" + arguments, "rb") as f:
                        spielzeug_lib.send_raw_data(f)
                else:
                    print(
                        "error",
                        binascii.b2a_base64(
                            "GOT unknown command '" + str(command) + "'"
                        ).decode(),
                    )
            except Exception as e:
                buf = io.StringIO()
                sys.print_exception(e, buf)
                print("error", binascii.b2a_base64(buf.getvalue()).decode())
        else:
            await asyncio.sleep_ms(100)
        await asyncio.sleep_ms(10)

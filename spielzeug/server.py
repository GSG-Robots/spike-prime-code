import asyncio
import binascii
import builtins
import hashlib
import io
import json
import os
import sys
import time

import color
import machine
from bleio import BLEIO

import hub


class Light:
    def __init__(self):
        self._turn_off_at = 0
        self._is_important = False

    def set_important(self):
        self._is_important = True

    def unset_important(self):
        self._is_important = False

    def delay_override(self, by_ms: int):
        self._turn_off_at = time.ticks_ms() + by_ms

    def should_turn_off(self):
        if self._turn_off_at and self._turn_off_at < time.ticks_ms():
            self._turn_off_at = 0
            return True
        return False

    def should_not_use(self):
        if self._turn_off_at and self._turn_off_at < time.ticks_ms():
            self._turn_off_at = 0
        return self._is_important or self._turn_off_at


class Remote:
    def send(self, packet_id: int | bytes, data: str | bytes):
        if not isinstance(data, bytes):
            data = data.encode()
        BLEIO.send_packet(packet_id, data)

    def error(self, e):
        send_error(e, b"E")


light = Light()
remote = Remote()


def send_error(e: Exception, symbol=b"!"):
    buf = io.StringIO()
    sys.print_exception(e, buf)
    BLEIO.send_packet(symbol, buf.getvalue())


def recursive_listdir(path: str):
    for pth, typ, *_ in os.ilistdir(path):
        apth = path + "/" + pth
        if typ == 32768:
            yield apth
        elif typ == 16384:
            yield apth
            yield from recursive_listdir(apth)
        else:
            assert False


def remove(path: str):
    path = "/flash/src" + path
    print(path)
    typ = os.stat(path)[0]
    if typ == 32768:
        os.remove(path)
    elif typ == 16384:
        for p in recursive_listdir(path):
            remove(p[10:])
        os.rmdir(path)
    else:
        assert False


prog_task = None
has_stopped = asyncio.Event()
has_stopped.set()


async def program_wrapper(program):
    has_stopped.clear()
    try:
        await program
    except Exception as e:
        send_error(e, b"E")
        hub.light.color(hub.light.CONNECT, color.RED)
        light.delay_override(1000)
        hub.light.color(hub.light.POWER, color.RED)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.RED)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
    finally:
        hub.light_matrix.clear()
        hub.light.color(hub.light.POWER, color.WHITE)
        has_stopped.set()


async def start_program():
    global prog_task
    if prog_task:
        prog_task.cancel()
        await has_stopped.wait()
    for module in sys.modules.keys():
        if module == "src" or module.startswith("src."):
            del sys.modules[module]
    hub.light_matrix.clear()
    try:
        module = __import__("src")
    except Exception as e:
        send_error(e, b"E")
        hub.light.color(hub.light.CONNECT, color.MAGENTA)
        light.delay_override(1000)
        hub.light.color(hub.light.POWER, color.MAGENTA)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.MAGENTA)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.WHITE)
    if hasattr(module, "loop"):
        prog_task = asyncio.create_task(program_wrapper(module.loop()))
    else:
        remote.send(b"E", "You must define a function called 'loop' in '__init__.py'!")
        hub.light.color(hub.light.CONNECT, color.PURPLE)
        light.delay_override(1000)
        hub.light.color(hub.light.POWER, color.PURPLE)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.PURPLE)
        await asyncio.sleep_ms(100)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.WHITE)


async def kill_program():
    if prog_task:
        prog_task.cancel()
        await has_stopped.wait()


def remote_print(*args, sep=" "):
    data = sep.join(x if isinstance(x, str) else repr(x) for x in args).encode()
    BLEIO.send_packet(b"P", data)


async def handle_connect_button():
    global off
    while True:
        if light.should_turn_off():
            hub.light.color(hub.light.CONNECT, color.BLACK)
        elif not light.should_not_use():
            if BLEIO.is_connected():
                hub.light.color(hub.light.CONNECT, color.BLUE)
            elif BLEIO.is_advertising():
                if time.ticks_ms() % 1350 < 150:
                    hub.light.color(hub.light.CONNECT, color.BLUE)
                    hub.sound.beep(500, 50)
                    await asyncio.sleep_ms(50)
                    hub.light.color(hub.light.CONNECT, color.BLACK)
                    await asyncio.sleep_ms(40)
                    hub.light.color(hub.light.CONNECT, color.BLUE)
                    hub.sound.beep(500, 60)
                    await asyncio.sleep_ms(60)
                    hub.light.color(hub.light.CONNECT, color.BLACK)
            else:
                hub.light.color(hub.light.CONNECT, color.BLACK)
        if hub.button.pressed(hub.button.CONNECT):
            hub.sound.beep(500, 100)
            if not light.should_not_use():
                if BLEIO.is_connected():
                    hub.light.color(hub.light.CONNECT, color.AZURE)
                else:
                    hub.light.color(hub.light.CONNECT, color.BLUE)
            took = 0
            while hub.button.pressed(hub.button.CONNECT):
                await asyncio.sleep_ms(100)
                took += 1
                if took > 30:
                    break
            else:
                if not light.should_not_use():
                    hub.light.color(hub.light.CONNECT, color.BLACK)
                if BLEIO.is_advertising():
                    BLEIO.stop_advertising()
                elif BLEIO.is_connected():
                    BLEIO.disconnect()
                else:
                    BLEIO.start_advertising()
                await asyncio.sleep_ms(160)
                continue
            hub.sound.beep(700, 50)
            time.sleep(0.1)
            hub.sound.beep(700, 200)
            hub.light.color(hub.light.CONNECT, color.PURPLE)
            while hub.button.pressed(hub.button.CONNECT):
                if hub.button.pressed(hub.button.LEFT):
                    hub.light.color(hub.light.CONNECT, color.GREEN)
                    hub.sound.beep(800, 400)
                    time.sleep(0.4)
                    machine.reset()
                    break
                if hub.button.pressed(hub.button.RIGHT):
                    hub.light.color(hub.light.CONNECT, color.GREEN)
                    hub.sound.beep(800, 400)
                    time.sleep(0.4)
                    sys.exit()
                    break
                if hub.button.pressed(hub.button.POWER):
                    hub.light.color(hub.light.CONNECT, color.GREEN)
                    hub.sound.beep(800, 400)
                    time.sleep(0.1)
                    if not has_stopped.is_set():
                        hub.sound.beep(400, 1000)
                        break
                    await start_program()
                    break
            hub.light.color(hub.light.CONNECT, color.BLACK)
            while hub.button.pressed(hub.button.CONNECT):
                await asyncio.sleep_ms(100)
        await asyncio.sleep_ms(10)


async def main():
    # Modify builtins
    builtins.oprint = builtins.print
    builtins.print = remote_print
    builtins.remote = remote

    # Init
    hub.light.color(hub.light.POWER, color.ORANGE)
    try:
        os.mkdir("/flash/src")
    except OSError:
        pass
    setup_ble_server()
    # await start_program()

    # Initialized, start main loop
    hub.light.color(hub.light.POWER, color.WHITE)
    await handle_connect_button()

    # Deinit
    builtins.print = _print
    del builtins.remote
    del builtins.oprint


def setup_ble_server():
    all_paths = []
    current_file = None
    current_buffer = b""

    def handle_packet():
        hub.light.color(hub.light.CONNECT, color.GREEN)
        light.delay_override(50)

    @BLEIO.handles(b"Y")
    def start_sync(data: bytes):
        nonlocal all_paths
        handle_packet()
        all_paths = list(a[10:] for a in recursive_listdir("/flash/src"))
        print(all_paths)
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"$")
    def cancel_sync(data: bytes):
        nonlocal all_paths
        handle_packet()
        all_paths.clear()
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"N")
    def finish_sync(data: bytes):
        nonlocal all_paths
        handle_packet()
        print(all_paths)
        for path in all_paths:
            remove(path)
        all_paths.clear()
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"D")
    def sync_directory(data: bytes):
        handle_packet()
        args = data.decode()
        if args not in all_paths:
            try:
                os.mkdir("/flash/src" + args)
            except OSError:
                pass
        if args in all_paths:
            all_paths.remove(args)
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"F")
    def sync_file(data: bytes):
        nonlocal current_file, current_buffer
        handle_packet()
        args = data.decode()
        name, hash = args.split(" ", 1)
        assert name[0] == "/"
        try:
            with open("/flash/src" + name, "rb") as f:
                old_hash = binascii.hexlify(hashlib.sha256(f.read()).digest()).decode()
        except OSError:
            old_hash = None

        if name in all_paths:
            all_paths.remove(name)
        oprint(old_hash, "vs", hash, "from", args)
        if old_hash != hash:
            current_file = "/flash/src" + name
            current_buffer = b""
            BLEIO.send_packet(b"U")
        else:
            BLEIO.send_packet(b"K")

    @BLEIO.handles(b"C")
    def read_file_chunk(data: bytes):
        nonlocal current_buffer
        handle_packet()
        current_buffer += data
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"E")
    def close_file(data: bytes):
        nonlocal current_buffer, current_file
        handle_packet()
        if current_file is None:
            return
        with open(current_file, "wb") as f:
            f.write(current_buffer)
        current_buffer = b""
        current_file = None
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"R")
    def remove_any(data: bytes):
        handle_packet()
        args = data.decode()
        remove(args)

    @BLEIO.handles(b"P")
    def start(data: bytes):
        handle_packet()
        asyncio.create_task(start_program())
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"X")
    def stop(data: bytes):
        handle_packet()
        asyncio.create_task(kill_program())
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"=")
    def echo(data: bytes):
        handle_packet()
        BLEIO.send_packet(b"=", data)

    @BLEIO.handles(b"&")
    def reboot(data: bytes):
        handle_packet()
        machine.reset()

    def handle_error(cmd, cause=None) -> None:
        hub.light.color(hub.light.CONNECT, color.RED)
        hub.sound.beep(350, 225)
        light.delay_override(225)
        if cause is None:
            BLEIO.send_packet(b"!", f"Unkown command {cmd}".encode())
        else:
            BLEIO.send_packet(b"!", f"Could not handle command {cmd}".encode())
            remote.error(cause)

    BLEIO._error_handler = handle_error

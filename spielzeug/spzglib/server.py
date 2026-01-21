import asyncio
import binascii
import builtins
import gc
import hashlib
import io
import os
import sys
import time
import zlib

import color
import hub
import machine

from .bleio import BLEIO
from .identify import loop as identify_program
from .version import FEATURE_LEVEL, PROTOCOL_VERSION

gc.enable()
gc.collect()


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
        if apth == "/flash/src":
            continue
        if typ == 32768:
            yield apth
        elif typ == 16384:
            yield from recursive_listdir(apth)
            yield apth
        else:
            raise RuntimeError


FILE = 32768
DIR = 16384


def filetype(path: str):
    return os.stat(path)[0]


def listdir(path: str):
    return [path + "/" + subpath for subpath, *_ in os.ilistdir(path)]


def remove(path: str):
    typ = filetype(path)
    if typ == FILE:
        os.remove(path)
    elif typ == DIR:
        for subpath in listdir(path):
            # This should never happen!
            remove(subpath)
        os.rmdir(path)
    else:
        raise RuntimeError


prog_task = None
has_stopped = asyncio.Event()
has_stopped.set()


async def program_wrapper(program):
    has_stopped.clear()
    try:
        await program
    except Exception as e:
        send_error(e, b"E")
        hub.light_matrix.show(
            [
                100,
                100,
                100,
                0,
                0,
                100,
                0,
                0,
                0,
                30,
                100,
                100,
                0,
                0,
                30,
                100,
                0,
                0,
                0,
                100,
                100,
                100,
                100,
                0,
                0,
            ],
        )
        hub.light.color(hub.light.CONNECT, color.RED)
        light.delay_override(1000)
        for _ in range(5):
            hub.sound.beep(200, 25)
            hub.light.color(hub.light.POWER, color.RED)
            await asyncio.sleep_ms(100)
            hub.light.color(hub.light.POWER, color.BLACK)
            await asyncio.sleep_ms(50)
    finally:
        hub.light_matrix.clear()
        hub.light.color(hub.light.POWER, color.WHITE)
        has_stopped.set()


async def start_internal_program(prog_loop_coro):
    global prog_task
    await kill_program()
    prog_task = asyncio.create_task(program_wrapper(prog_loop_coro))


async def start_program():
    gc.collect()
    global prog_task
    await kill_program()
    for module in sys.modules:
        if module == "src" or module.startswith("src."):
            del sys.modules[module]
    hub.light_matrix.clear()
    try:
        module = __import__("src")
    except Exception as e:
        send_error(e, b"E")
        hub.light_matrix.show(
            [
                100,
                100,
                100,
                0,
                0,
                100,
                0,
                0,
                0,
                100,
                100,
                100,
                0,
                0,
                30,
                100,
                0,
                0,
                0,
                30,
                100,
                100,
                100,
                0,
                0,
            ],
        )
        hub.light.color(hub.light.CONNECT, color.MAGENTA)
        light.delay_override(1000)
        for _ in range(5):
            hub.sound.beep(400, 90)
            hub.light.color(hub.light.POWER, color.MAGENTA)
            await asyncio.sleep_ms(100)
            hub.sound.beep(400, 40)
            hub.light.color(hub.light.POWER, color.BLACK)
            await asyncio.sleep_ms(50)

        hub.light.color(hub.light.POWER, color.WHITE)
        return
    if hasattr(module, "loop"):
        prog_task = asyncio.create_task(program_wrapper(module.loop()))
    else:
        remote.send(b"E", "You must define a function called 'loop' in '__init__.py'!")
        hub.light_matrix.show(
            [
                100,
                100,
                100,
                0,
                0,
                100,
                0,
                0,
                0,
                30,
                100,
                100,
                0,
                0,
                100,
                100,
                0,
                0,
                0,
                30,
                100,
                100,
                100,
                0,
                0,
            ],
        )
        hub.light.color(hub.light.CONNECT, color.PURPLE)
        light.delay_override(1000)
        for _ in range(5):
            hub.sound.beep(475, 100)
            hub.light.color(hub.light.POWER, color.PURPLE)
            await asyncio.sleep_ms(100)
            hub.sound.beep(600, 50)
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
    advertised = 0
    while True:
        if light.should_turn_off():
            hub.light.color(hub.light.CONNECT, color.BLACK)
        elif not light.should_not_use():
            if BLEIO.is_connected():
                hub.light.color(hub.light.CONNECT, color.BLUE)
                advertised = 0
            elif BLEIO.is_advertising():
                if time.ticks_ms() % 1350 < 150:
                    hub.light.color(hub.light.CONNECT, color.BLUE)
                    if advertised < 10:
                        hub.sound.beep(500, 50)
                    await asyncio.sleep_ms(50)
                    hub.light.color(hub.light.CONNECT, color.BLACK)
                    await asyncio.sleep_ms(40)
                    hub.light.color(hub.light.CONNECT, color.BLUE)
                    if advertised < 10:
                        hub.sound.beep(500, 60)
                    await asyncio.sleep_ms(60)
                    hub.light.color(hub.light.CONNECT, color.BLACK)
                    advertised += 1
            else:
                hub.light.color(hub.light.CONNECT, color.BLACK)
                advertised = 0
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
                if took > 10:
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
                    import _system.default
                    del sys.modules["_system.default"]
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
    builtins.serial_print = builtins.print
    builtins.print = remote_print
    builtins.remote = remote

    # Init
    hub.light.color(hub.light.POWER, color.ORANGE)
    hub.light_matrix.show(
        [
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            100,
            0,
            100,
            0,
            100,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
            0,
        ]
    )
    try:
        os.mkdir("/flash/src")
    except OSError:
        pass
    setup_ble_server()
    if not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT)):
        await asyncio.sleep_ms(1500)
        await start_program()

    # Initialized, start main loop
    hub.light.color(hub.light.POWER, color.WHITE)
    await handle_connect_button()

    # Deinit
    builtins.print = builtins.serial_print
    del builtins.remote
    del builtins.serial_print


def setup_ble_server():
    transfer_scope = "/flash/src"
    all_paths = []
    current_file = None
    current_buffer = b""

    BLEIO.start_advertising()

    def handle_packet():
        hub.light.color(hub.light.CONNECT, color.GREEN)
        light.delay_override(50)

    @BLEIO.handles(b"V")
    def version(data: bytes):
        nonlocal all_paths
        handle_packet()
        BLEIO.send_packet(b"V" + PROTOCOL_VERSION.to_bytes(2, "big") + FEATURE_LEVEL.to_bytes(2, "big"))

    @BLEIO.handles(b"Y")
    def start_sync(data: bytes):
        nonlocal all_paths, transfer_scope
        handle_packet()
        if data == b"":
            transfer_scope = "/flash/src"
        elif data == b"firmware-update":
            transfer_scope = "/flash"
        else:
            BLEIO.send_packet(b"!", b"Unknown sync mode!")
            return
        all_paths = list(a[len(transfer_scope) :] for a in recursive_listdir(transfer_scope))
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
        for path in all_paths:
            remove(transfer_scope + path)
        all_paths.clear()
        BLEIO.send_packet(b"K")

    @BLEIO.handles(packet_id=b"D")
    def sync_directory(data: bytes):
        handle_packet()
        args = data.decode()
        assert args[0] == "/"
        if args not in all_paths:
            try:
                os.mkdir(transfer_scope + args)
            except OSError:
                print("!!!", args, all_paths)
                ...
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
            with open(transfer_scope + name, "rb") as f:
                old_hash = binascii.hexlify(hashlib.sha256(f.read()).digest()).decode()
        except OSError:
            old_hash = None

        if name in all_paths:
            all_paths.remove(name)
        if old_hash != hash:
            current_file = transfer_scope + name
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
        gc.collect()
        with open(current_file, "wb") as f:
            f.write(zlib.decompress(binascii.a2b_base64(current_buffer)))
        current_buffer = b""
        current_file = None
        gc.collect()
        BLEIO.send_packet(b"K")

    @BLEIO.handles(b"R")
    def remove_any(data: bytes):
        handle_packet()
        args = data.decode()
        remove(transfer_scope + args)

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

    @BLEIO.handles(b"I")
    def identify(data: bytes):
        handle_packet()
        asyncio.create_task(start_internal_program(identify_program()))
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

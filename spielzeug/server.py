import asyncio
import binascii
import builtins
import hashlib
import io
import json
import os
import select
import sys
import time

import machine
import color
import hub
from bleio import BLE_UART

try:
    os.mkdir("/flash/src")
except OSError:
    pass

off = 0
important = False


async def _read_decoded(io, ln):
    data = b""
    while len(data) < ln:
        await asyncio.sleep_ms(1)
        data += io.read(ln - len(data))
    if isinstance(data, bytes):
        return data.decode()
    return data


async def _get_next(
    timeout=-1,
    bin=False,
) -> tuple[str, str | bytes | None] | None:
    global off, important
    poll = select.poll()
    poll.register(BLE_UART.rx, select.POLLIN)
    poll.register(sys.stdin, select.POLLIN)
    for stdin, _ in poll.poll(timeout):
        hub.light.color(hub.light.CONNECT, color.YELLOW)
        important = True
        if await _read_decoded(stdin, 1) != ":":
            important = False
            await asyncio.sleep_ms(1)
            continue

        cmd = await _read_decoded(stdin, 1)
        nxt = await _read_decoded(stdin, 1)
        if nxt == "]":
            hub.light.color(hub.light.CONNECT, color.GREEN)
            off = time.ticks_ms() + 30
            important = False
            await asyncio.sleep_ms(1)
            return (cmd, None)
        else:
            hub.light.color(hub.light.CONNECT, color.ORANGE)
            try:
                ln = int(nxt + await _read_decoded(stdin, 3))
                arg = await _read_decoded(stdin, ln)
                decoded_arg = binascii.a2b_base64(arg)
                if not bin:
                    decoded_arg = decoded_arg.decode()
            except Exception as e:
                write_error(e)
                hub.light.color(hub.light.CONNECT, color.RED)
                hub.sound.beep(300, 225)
                off = time.ticks_ms() + 225
                important = False
                await asyncio.sleep_ms(1)
                return None
            hub.light.color(hub.light.CONNECT, color.GREEN)
            off = time.ticks_ms() + 30
            important = False
            await asyncio.sleep_ms(1)
            return cmd, decoded_arg
    await asyncio.sleep_ms(1)
    return None


async def get_next(bin=False):
    while True:
        result = await _get_next(0, bin)
        if not result:
            await asyncio.sleep_ms(100)
            continue
        return result


def write(cmd, args=None):
    msg = ":" + cmd
    if args is not None:
        encoded_args = binascii.b2a_base64(args, newline=False)
        msg += ("0000" + str(len(encoded_args)))[-4:] + encoded_args.decode()
    else:
        msg += "]"
    sys.stdout.write(msg)
    BLE_UART.write(msg)


class Remote:
    def send(self, *args, **kwargs):
        write(*args, **kwargs)

    def block(self):
        write("B")

    def unblock(self):
        write("D")

    def error(self, e):
        write_error(e, "E")


builtins.remote = Remote()


def write_error(e: Exception, symbol="!"):
    buf = io.StringIO()
    sys.print_exception(e, buf)
    write(symbol, buf.getvalue())


def OK():
    write("K")


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
    typ = os.stat(path)[0]
    if typ == 32768:
        os.remove(path)
    elif typ == 16384:
        for p in recursive_listdir(path):
            remove(p)
        os.rmdir(path)
    else:
        assert False


async def read_file(file_name):
    with open("/flash/src" + file_name, "wb+") as f:
        while True:
            await asyncio.sleep_ms(1)
            cmd, args = await get_next(True)
            if cmd == "C":
                f.write(args)
                OK()
            elif cmd == "E":
                break
            elif cmd == ">":
                sys.exit()
            elif cmd == "$":
                return
            elif cmd == "=":
                return
            else:
                write("!", "Unkown command %s" % cmd)


prog_task = None
has_stopped = asyncio.Event()
has_stopped.set()

async def program_wrapper(program):
    has_stopped.clear()
    try:
        await program
    except Exception as e:
        write_error(e, "E")
        hub.light.color(hub.light.POWER, color.RED)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.RED)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
    finally:
        hub.light_matrix.clear()
        hub.light.color(hub.light.POWER, color.WHITE)
        has_stopped.set()


async def run_program():
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
        write_error(e, "E")
        hub.light.color(hub.light.POWER, color.MAGENTA)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.MAGENTA)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.WHITE)
    if hasattr(module, "loop"):
        prog_task = asyncio.create_task(program_wrapper(module.loop()))
    else:
        write("E", "You must define a function called 'loop' in '__init__.py'!")
        hub.light.color(hub.light.POWER, color.PURPLE)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.MAGENTA)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.BLACK)
        await asyncio.sleep_ms(50)
        hub.light.color(hub.light.POWER, color.WHITE)


async def kill_program():
    if prog_task:
        prog_task.cancel()
        await has_stopped.wait()


def remote_print(*args, **kwargs):
    write(
        "P",
        json.dumps(
            (
                tuple(a if isinstance(a, str) else repr(a) for a in args),
                {
                    key: a if isinstance(a, str) else repr(a)
                    for key, a in kwargs.items()
                },
            )
        ),
    )


async def handle_connect_button():
    global off
    while True:
        if off and time.ticks_ms() > off:
            hub.light.color(hub.light.CONNECT, color.BLACK)
            off = 0
        elif not off and not important:
            if BLE_UART.is_connected():
                hub.light.color(hub.light.CONNECT, color.BLUE)
            elif BLE_UART.is_advertising():
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
            if not important:
                if BLE_UART.is_connected():
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
                if not important:
                    hub.light.color(hub.light.CONNECT, color.BLACK)
                if BLE_UART.is_advertising():
                    BLE_UART.stop_advertising()
                elif BLE_UART.is_connected():
                    BLE_UART.disconnect()
                else:
                    BLE_UART.start_advertising()
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
                    machine.soft_reset()
                    break
                if hub.button.pressed(hub.button.POWER):
                    hub.light.color(hub.light.CONNECT, color.GREEN)
                    hub.sound.beep(800, 400)
                    time.sleep(0.1)
                    if not has_stopped.is_set():
                        hub.sound.beep(400, 1000)
                        break
                    await run_program()
                    break
            hub.light.color(hub.light.CONNECT, color.BLACK)
            while hub.button.pressed(hub.button.CONNECT):
                await asyncio.sleep_ms(100)
        await asyncio.sleep_ms(10)


async def main():
    _print = builtins.print
    builtins.print = remote_print
    hub.light.color(hub.light.POWER, color.WHITE)
    task = asyncio.create_task(handle_connect_button())
    # await run_program()
    await server()
    task.cancel()
    builtins.print = _print


async def server():
    all_paths = []
    global off

    while True:
        try:
            cmd, args = await get_next()
            if cmd == "Y":
                all_paths = list(a[10:] for a in recursive_listdir("/flash/src"))
                OK()
            elif cmd == "F":
                assert args is not None
                name, hash = args.split(" ")
                assert name[0] == "/"
                try:
                    with open("/flash/src" + name, "rb") as f:
                        old_hash = binascii.hexlify(
                            hashlib.sha256(f.read()).digest()
                        ).decode()
                except OSError:
                    old_hash = None

                if old_hash != hash:
                    write("U")
                    await read_file(name)
                if name in all_paths:
                    all_paths.remove(name)
                OK()
            elif cmd == "D":
                assert args is not None
                if args not in all_paths:
                    try:
                        os.mkdir("/flash/src" + args)
                    except OSError:
                        pass
                if args in all_paths:
                    all_paths.remove(args)
                OK()
            elif cmd == "N":
                for path in all_paths:
                    remove(path)
                all_paths = []
                OK()
            elif cmd == "R":
                assert args is not None
                remove(args)
                OK()
            elif cmd == "P":
                await run_program()
                OK()
            elif cmd == "X":
                await kill_program()
                OK()
            elif cmd == "&":
                machine.reset()
                OK()
            elif cmd == "=":
                write("=", args)
            elif cmd == ">":
                break
            elif cmd == "$":
                all_paths = []
                OK()
            else:
                hub.light.color(hub.light.CONNECT, color.RED)
                hub.sound.beep(350, 225)
                off = time.ticks_ms() + 225
                write("!", f"Unkown command {cmd}")
        except Exception as e:
            write_error(e)

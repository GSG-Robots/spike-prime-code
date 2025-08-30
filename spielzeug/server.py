import asyncio
import binascii
import builtins
import hashlib
import io
import json
import os

import machine
import select
import sys
import hub


try:
    os.mkdir("/flash/src")
except OSError:
    pass


def _get_next(
    timeout=-1,
    bin=False,
) -> tuple[str, str | bytes | None] | None:
    poll = select.poll()
    poll.register(sys.stdin, select.POLLIN)
    for stdin, _ in poll.poll(timeout):
        while stdin.read(1) != ":":
            ...

        cmd = stdin.read(1)
        nxt = stdin.read(1)
        if nxt == "]":
            return (cmd, None)
        else:
            ln = int(nxt + stdin.read(3))
            arg = stdin.read(ln)
            try:
                decoded_arg = binascii.a2b_base64(arg)
                if not bin:
                    decoded_arg = decoded_arg.decode()
            except Exception as e:
                write_error(e)
                return None
            return cmd, decoded_arg
    return None


async def get_next(bin=False):
    while True:
        result = _get_next(0, bin)
        if not result:
            await asyncio.sleep_ms(100)
            continue
        return result


def write(cmd, args=None):
    sys.stdout.write(":" + cmd)
    if args is not None:
        encoded_args = binascii.b2a_base64(args, newline=False)
        sys.stdout.write(("0000" + str(len(encoded_args)))[-4:])
        sys.stdout.write(encoded_args.decode())
    else:
        sys.stdout.write("]")


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
        os.rmdir(path)
    else:
        assert False


async def read_file(file_name):
    with open("/flash/src" + file_name, "wb+") as f:
        while True:
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


async def program_wrapper(program):
    has_stopped.clear()
    try:
        try:
            await program
        except Exception as e:
            write_error(e)
    finally:
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
        write_error(e)
    if hasattr(module, "loop"):
        prog_task = asyncio.create_task(program_wrapper(module.loop()))
    else:
        write("!", "You must define a function called 'loop' in '__init__.py'!")


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


async def server():
    original_print = print
    builtins.print = remote_print
    all_paths = []

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
                write("!", f"Unkown command {cmd}")
        except Exception as e:
            write_error(e)
    builtins.print = original_print

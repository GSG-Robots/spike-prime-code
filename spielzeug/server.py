import asyncio
import binascii
import hashlib
import io
import os
import machine
import select
import sys


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


def write_error(e: Exception):
    buf = io.StringIO()
    sys.print_exception(e, buf)
    write("!", buf.getvalue())


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
    typ = os.stat("/flash/src" +path)[0]
    if typ == 32768:
        os.remove(path)
    elif typ == 16384:
        os.rmdir(path)
    else:
        assert False


async def read_file(file_name):
    with open(file_name, "wb+") as f:
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
            else:
                write("!", "Unkown command %s" % cmd)


async def server():
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
                    await read_file("main.py")
                if args in all_paths:
                    all_paths.remove(args)
                OK()
            elif cmd == "D":
                assert args is not None
                if args not in all_paths:
                    os.mkdir(args)
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
            elif cmd == "A":
                assert args is not None
                os.mkdir(args)
                OK()
            elif cmd == "P":
                ...
                OK()
            elif cmd == "X":
                ...
                OK()
            elif cmd == "&":
                machine.reset()
                OK()
            elif cmd == ">":
                return
            elif cmd == "$":
                all_paths = []
                OK()
            else:
                write("!", "Unkown command %s" % cmd)
        except Exception as e:
            write_error(e)

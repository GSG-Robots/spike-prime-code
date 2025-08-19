import binascii
import time

ser = None
timeout = 5


def set_ser(new_ser, new_timeout=5):
    global ser, timeout

    ser = new_ser
    timeout = new_timeout


def intake_raw_data(cb=None):
    start = time.time()
    data = b""
    while start + timeout > time.time():
        cmd = ser.readline()
        if not cmd:
            continue
        cmd = cmd.strip().decode()
        if cmd == "EOF":
            break
        elif cmd.startswith("CHUNK "):
            data += binascii.a2b_base64(cmd[6:])
            start = time.time()
            send_command("DIG")
        elif cmd.startswith("error "):
            raise RuntimeError(binascii.a2b_base64(cmd[6:]).decode())
        if cb is not None:
            cb()
    else:
        raise TimeoutError
    return data


def wait_for_keyword(keyword):
    start = time.time()
    while start + timeout > time.time():
        cmd = ser.readline()
        if not cmd:
            continue
        cmd = cmd.strip().decode()
        if cmd.startswith(keyword):
            break
        if cmd.startswith("error "):
            try:
                raise RuntimeError(binascii.a2b_base64(cmd[6:]).decode())
            except RuntimeError as e:
                raise e
            except:
                raise RuntimeError(cmd[6:])
    else:
        raise TimeoutError
    return cmd[len(keyword) :].strip()


def send_raw_data(data, cb=None):
    while True:
        chunk = data.read(192)
        if not chunk:
            break
        send_command("CHUNK", binascii.b2a_base64(chunk).decode())
        wait_for_keyword("DIG")
        if cb is not None:
            cb()
    send_command("EOF")
    return data


def send_command(*command):
    ser.write(" ".join(command).encode() + b"\n")


def get_command():
    data = ser.readline()
    if not data:
        return None, None
    data = data.decode().strip()
    command, arguments = data.split(" ", 1) if " " in data else (data, "")
    if command == "error":
        raise RuntimeError(binascii.a2b_base64(arguments).decode())
    return command, arguments

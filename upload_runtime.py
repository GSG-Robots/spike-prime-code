import base64
import os
import time
from pathlib import Path

import serial.tools.list_ports
import serial.tools.list_ports_windows
from tqdm import tqdm


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


def wait_for_prompt(ser):
    buf = b""
    start_time = time.time()
    elapsed = 0
    while elapsed < 1:
        c = ser.in_waiting
        ser.timeout = 1 - elapsed
        x = ser.read(c if c else 1)
        buf = (buf + x)[-5:]
        if buf == b"\n>>> ":
            return
        if buf == b"\n=== ":
            return
        elapsed = time.time() - start_time
    raise ConnectionError(
        "failed to get to the command prompt (last characters: %s)" % buf
    )


def write_command(ser, cmd, no_wait=False):
    ser.write(cmd + b"\r\n")
    if not no_wait:
        wait_for_prompt(ser)


def upload_runtime(from_folder="onboard"):
    serial = get_device()
    write_command(serial, b"\x03", no_wait=True)
    write_command(serial, b"\x02", no_wait=True)
    write_command(serial, b"")

    write_command(serial, b"import os")
    write_command(serial, b"import hub")
    write_command(serial, b"import ubinascii")

    # serial.write(b"\x05")
    # write_command(serial, b"def clean_dir(dir):", no_wait=True)
    # write_command(serial, b"    for file in os.listdir(dir):", no_wait=True)
    # write_command(serial, b"        print('-', dir + '/' + file)", no_wait=True)
    # write_command(serial, b"        try:", no_wait=True)
    # write_command(serial, b"            if (os.stat(dir + '/' + file)[0] & 0x4000) != 0:", no_wait=True)
    # write_command(serial, b"                print('as fold')", no_wait=True)
    # write_command(serial, b"                clean_dir(dir + '/' + file)", no_wait=True)
    # write_command(serial, b"                os.rmdir(dir + '/' + file)", no_wait=True)
    # write_command(serial, b"            else:", no_wait=True)
    # write_command(serial, b"                os.remove(dir + '/' + file)", no_wait=True)
    # write_command(serial, b"        except Exception as e:", no_wait=True)
    # write_command(serial, b"            print('!', dir + '/' + file, e)", no_wait=True)
    # write_command(serial, b"clean_dir('')", no_wait=True)
    # serial.write(b"\x04")
    # serial.write(b"\r\n")
    # serial.write(b"\r\n")
    # serial.write(b"\r\n")

    # return

    # time.sleep(3)

    for file in Path(from_folder).rglob("*"):
        print(file.relative_to(from_folder))
        if file.is_dir():
            write_command(
                serial,
                f"os.mkdir('{file.relative_to(from_folder).as_posix()}')".encode(),
            )
            continue
        write_command(
            serial,
            f"f = open('/{file.relative_to(from_folder).as_posix()}', 'wb')\r\n".encode(),
            no_wait=True,
        )
        wait_for_prompt(serial)
        with tqdm(total=os.path.getsize(str(file)), unit="B", unit_scale=True) as pbar:
            with file.absolute().open("rb") as f:
                byte = f.read(192)
                while len(byte) > 0:
                    write_command(
                        serial,
                        f"f.write(ubinascii.a2b_base64('{base64.b64encode(byte).decode()}'))".encode(),
                    )
                    pbar.update(len(byte))
                    byte = f.read(192)
        write_command(serial, b"f.close()")
    time.sleep(5)
    write_command(serial, b"hub.reset()", no_wait=True)


if __name__ == "__main__":
    upload_runtime("spielzeug")
    # get_device().write(b"\x03")

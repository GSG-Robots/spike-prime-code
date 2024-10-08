import sys
import serial.tools.list_ports_windows
import tqdm
import subprocess
import colorama
import pathlib
from spike_prime_compyne import spike_prime_compyne
import msvcrt
import spikeapi


devices = serial.tools.list_ports_windows.comports()
if len(devices) == 0:
    print(colorama.Fore.RED + "No devices found" + colorama.Fore.RESET)
    sys.exit(1)
if len(devices) == 1:
    device_choice = devices[0]
else:
    for index, device in enumerate(devices):
        print(f"{index+1:>2}. {device.device}")
    device_choice = devices[int(input("Device: ")) - 1]

device = spikeapi.Device(device_choice.device)

slot = 0
file = pathlib.Path(sys.argv[1])

# Step 1: ComPYning
print(colorama.Fore.GREEN + "> ComPYning..." + colorama.Fore.RESET)
comPYned: str = spike_prime_compyne(file, slot=slot)
file.with_suffix(".cpyd.py").write_text(comPYned)

# Step 2: Compiling
print(colorama.Fore.GREEN + "> Compiling...", end="")
proc = subprocess.run(["mpy-cross-v5", file.with_suffix(".cpyd.py")])
mpy = file.with_suffix(".cpyd.mpy").read_bytes()
file.with_suffix(".cpyd.mpy").unlink()
print(" done" + colorama.Fore.RESET)

# Step 3: Uploading
print(colorama.Fore.GREEN + "> Uploading..." + colorama.Fore.RESET)
progress_bar = tqdm.tqdm(total=100, unit="B", unit_scale=True)


def callback(done, total, bs):
    progress_bar.total = total * bs
    progress_bar.update(done * bs - progress_bar.n)


device.upload_file(
    mpy,
    slot,
    sys.argv[1],
    filename="__init__.mpy",
    callback=callback,
)

progress_bar.close()

# Step 4: Running
print(colorama.Fore.GREEN + "> Running..." + colorama.Fore.RESET)
device.run_program(slot)

while not device.running_program:
    pass

print(colorama.Fore.CYAN + ">> Press any key to exit" + colorama.Fore.RESET)

# Step 5: Monitoring
while True:
    if not device.active:
        print(colorama.Fore.GREEN + "> Device disconnected" + colorama.Fore.RESET)
        break
    if device.logs:
        log = device.logs.popleft()
        if log.type == spikeapi.LogType.PRINT:
            print(colorama.Fore.LIGHTBLACK_EX + log.entry + colorama.Fore.RESET)
        if log.type == spikeapi.LogType.USER_PROGRAM_PRINT:
            print(log.entry)
        elif log.type == spikeapi.LogType.USER_PROGRAM_ERROR:
            print(colorama.Fore.RED + log.entry + colorama.Fore.RESET)
        elif log.type == spikeapi.LogType.RUNTIME_ERROR:
            print(colorama.Fore.YELLOW + log.entry + colorama.Fore.RESET)

    # if not device.running_program:
    #     print(colorama.Fore.GREEN + "> Program finished" + colorama.Fore.RESET)
    #     break
    if msvcrt.kbhit():
        print(
            colorama.Fore.LIGHTGREEN_EX
            + "> Got input. Exiting..."
            + colorama.Fore.RESET
        )
        break

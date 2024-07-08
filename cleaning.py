# LEGO type:standard slot:3 autostart
from spike import Motor, PrimeHub
import spike.control
import random
hub = PrimeHub()

def all_motors(func):
    for port in ("A", "B", "C", "D", "E", "F", ):
        try:
            func(Motor(port))
        except RuntimeError:
            continue

def _run(power):
    all_motors(lambda motor: motor.start_at_power(power))
    while True:
        spike.control.wait_for_seconds(0.1)


def run(power):
    try:
        _run(power)
    except KeyboardInterrupt:
        ...
    except SystemExit:
        ...
    while True:
        try:
            all_motors(lambda motor: motor.stop())
            spike.control.wait_for_seconds(2)
            break
        except KeyboardInterrupt:
            ...
        except SystemExit:
            ...

run(100)
while True:
    run(-random.randint(50, 100))
    run(random.randint(50, 100))

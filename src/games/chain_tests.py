# LEGO type:standard slot:15 autostart

import time
from spike import PrimeHub, Motor

spike = PrimeHub()
motor = Motor("A")

try:
    while True:
        for x in range(4):
            motor.run_to_position((x * 90) % 360, "clockwise", 100)
            print((x * 90) % 360)
            time.sleep(.5)



except KeyboardInterrupt:
    raise SystemExit


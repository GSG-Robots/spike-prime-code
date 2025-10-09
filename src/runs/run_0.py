import time
import color as col
from ..gsgr.enums import Pivot

from ..gsgr.conditions import cm, sec
from ..gsgr.movement import (
    gyro_drive,
    gyro_turn,
    gyro_wall_align,
)

display_as = 0
color = col.RED


def run():
    # Set Gyro Origin
    import motor

    motor.run_to_absolute_position(0, 0, 100)
    motor.run_to_absolute_position(1, 0, 100)
    motor.run_to_absolute_position(2, 0, 100)
    motor.run_to_absolute_position(3, 0, 100)

    time.sleep(3)

    astart = motor.absolute_position(0)
    bstart = motor.absolute_position(1)
    cstart = motor.absolute_position(2)
    dstart = motor.absolute_position(3)

    motor.run(0, 305)
    motor.run(1, 295)
    motor.run(2, 300)
    motor.run(3, 299)

    time.sleep(10)

    motor.stop(0, stop=motor.HOLD)
    motor.stop(1, stop=motor.HOLD)
    motor.stop(2, stop=motor.HOLD)
    motor.stop(3, stop=motor.HOLD)

    time.sleep(1)

    aend = motor.absolute_position(0)
    bend = motor.absolute_position(1)
    cend = motor.absolute_position(2)
    dend = motor.absolute_position(3)

    print("A", aend - astart)
    print("B", bend - bstart)
    print("C", cend - cstart)
    print("D", dend - dstart)

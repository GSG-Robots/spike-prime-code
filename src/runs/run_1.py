import color as col

from ..gsgr.conditions import OR, cm, pickup, wheels_blocked
from ..gsgr.enums import Attachment
from ..gsgr.movement import gyro_drive, gyro_turn, gyro_wall_align, hold_attachment, run_attachment

display_as = 1
color = col.RED


def run():
    # Set Gyro Origin
    gyro_wall_align(0.3)
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(
        0,
        900,
        OR(wheels_blocked(), cm(86.4)),
        accelerate=10,
        decelerate=20,
    )
    run_attachment(Attachment.FRONT_RIGHT, 1000, 0.9, untension=25, stall=True)
    gyro_drive(10, -900, cm(8.5), accelerate=10, decelerate=30)
    gyro_turn(90, 150, timeout=2500)
    gyro_drive(90, -900, cm(27.5), accelerate=10, decelerate=30)
    gyro_drive(90, 900, cm(32), accelerate=10, decelerate=30)
    gyro_turn(10, 250, timeout=2500)
    gyro_drive(
        10,
        -1000,
        cm(37.5),
        brake=False,
        accelerate=10,
    )
    gyro_drive(
        45,
        -1000,
        pickup(cm(50)),
        brake=False,
        decelerate=40,
    )

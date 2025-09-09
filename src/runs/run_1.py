import color as col

from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
)

display_as = 1
color = col.RED


def run():
    # Set Gyro Origin
    gyro_wall_align(0.3)
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(
        0,
        900,
        impact(cm(86.4)),
        accelerate=10,
        decelerate=20,
    )
    run_attachment(Attachment.FRONT_RIGHT, 1000, 0.9, untension=25, stall=True)
    gyro_drive(
        10,
        -1000,
        cm(46),
        accelerate=10,
    )
    gyro_drive(
        45,
        -1000,
        pickup(cm(50)),
        brake=False,
        decelerate=40,
    )

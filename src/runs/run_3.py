import time

from src import hub

from ..gsgr.config import cfg
from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
)

import color as col

display_as = 3
color = col.RED


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(
        0,
        80,
        cm(75.84),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(-90)
    gyro_drive(
        -90,
        80,
        cm(9.6),
        accelerate=30,
        decelerate=60,
    )
    time.sleep(0.1)
    # TODO
    cfg.DRIVING_MOTORS.run_for_degrees(35, speed_0=0, speed_1=30)
    run_attachment(Attachment.FRONT_LEFT, -100, 2)
    gyro_turn(-90)
    gyro_drive(
        -90,
        -90,
        cm(4.8),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(-45)
    gyro_drive(
        -45,
        -90,
        cm(14.4),
        accelerate=10,
        decelerate=70,
    )
    gyro_turn(0, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(
        0,
        90,
        cm(67.2),
        accelerate=10,
        decelerate=0,
    )
    cfg.DRIVING_MOTORS.run_for_degrees(90, speed_0=0, speed_1=100)
    gyro_drive(
        -45,
        100,
        pickup(cm(50)),
        accelerate=0,
        decelerate=0,
    )

import time

import color as col
import motor

from ..gsgr.conditions import cm, pickup
from ..gsgr.config import cfg
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = 3
color = col.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(
        0,
        900,
        cm(62),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(90, pivot=Pivot.LEFT_WHEEL)
    gyro_drive(
        90,
        900,
        cm(3.5),
        accelerate=30,
        decelerate=60,
    )
    time.sleep(0.1)
    motor.run_for_degrees(cfg.LEFT_MOTOR, 35, 300)
    run_attachment(Attachment.FRONT_LEFT, -1000, 2)
    gyro_turn(90, pivot=Pivot.LEFT_WHEEL)
    gyro_drive(90, -900, cm(75), accelerate=10, decelerate=40)
    run_attachment(Attachment.BACK_RIGHT, -700, 1.2)
    gyro_drive(90, 800, cm(5), accelerate=10, decelerate=40)
    run_attachment(Attachment.BACK_RIGHT, 700, 1.3, untension=90)
    gyro_drive(90, 900, cm(50.5), accelerate=10, decelerate=40)
    run_attachment(Attachment.BACK_LEFT, -500, 1)
    gyro_turn(45, 100, Pivot.RIGHT_WHEEL)
    gyro_turn(-17, 100, Pivot.LEFT_WHEEL)
    gyro_drive(-17, 900, cm(20))
    gyro_turn(17, 100, Pivot.LEFT_WHEEL)
    gyro_drive(17, 900, pickup(cm(80)))

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
        800,
        cm(75.84),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(90)
    gyro_drive(
        90,
        800,
        cm(9.6),
        accelerate=30,
        decelerate=60,
    )
    time.sleep(0.1)
    motor.run_for_degrees(cfg.LEFT_MOTOR, 35, 300)
    run_attachment(Attachment.FRONT_LEFT, -1000, 2)
    gyro_turn(90)
    gyro_drive(
        90,
        -900,
        cm(4.8),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(45)
    gyro_drive(
        45,
        -900,
        cm(14.4),
        accelerate=10,
        decelerate=70,
    )
    gyro_turn(0, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(
        0,
        1000,
        cm(65.2),
        accelerate=10,
        decelerate=0,
    )
    motor.run_for_degrees(cfg.LEFT_MOTOR, 90, 100)
    gyro_drive(
        45,
        1000,
        pickup(cm(50)),
        accelerate=0,
        decelerate=0,
    )

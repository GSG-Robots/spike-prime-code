import time

import color as col
import motor

from ..gsgr.conditions import cm, impact
from ..gsgr.config import cfg
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, hold_attachment, run_attachment

display_as = 3
color = col.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(
        0,
        900,
        cm(67.5),
        accelerate=10,
        decelerate=40,
    )
    gyro_turn(90, pivot=Pivot.LEFT_WHEEL, timeout=2500)
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
    gyro_turn(90, pivot=Pivot.LEFT_WHEEL, timeout=2500)

    gyro_drive(90, -700, cm(25.6), accelerate=10, decelerate=20)
    gyro_drive(90, 400, cm(13), accelerate=10, decelerate=40)
    gyro_drive(90, -400, cm(6), accelerate=10, decelerate=40, brake=False)
    gyro_turn(8, 100, Pivot.LEFT_WHEEL, timeout=2500, brake=False)
    gyro_drive(8, 1000, impact(cm(100)))
    # gyro_turn()
    # gyro_drive(-90, 1000, impact(cm(30)))

    # gyro_drive(-17, 900, cm(20))
    # gyro_turn(17, 100, Pivot.LEFT_WHEEL, timeout=2500)
    # gyro_drive(17, 900, pickup(cm(80)))

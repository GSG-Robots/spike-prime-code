import time

import color as col
from ..gsgr.config import PID

from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = 2
color = col.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(
        0,
        900,
        impact(cm(35)),
        accelerate=10,
        decelerate=40,
    )
    gyro_drive(0, -75, cm(0.25), pid=PID(0, 0, 0))
    run_attachment(Attachment.FRONT_LEFT, 1000, 235, stall=True, when_i_say_duration_i_mean_degrees=True)
    time.sleep(0.2)
    gyro_drive(
        0,
        -600,
        cm(15.75),
        accelerate=30,
        decelerate=40,
        brake=False,
    )
    time.sleep(0.2)
    gyro_turn(-30)
    gyro_drive(
        -30,
        -1000,
        cm(10),
        accelerate=100,
        brake=False,
    )
    gyro_turn(
        25,
        200,
        tolerance=2,
        brake=False,
    )
    gyro_drive(
        35,
        -1000,
        pickup(cm(30)),
    )

import time

import color as col

from ..gsgr.conditions import cm
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    run_attachment,
)

display_as = 5
color = col.GREEN


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 800, cm(40), accelerate=10, decelerate=30)
    time.sleep(0.5)
    gyro_drive(0, -500, cm(10), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_RIGHT, -1000, 0.5)
    gyro_drive(0, 350, cm(15), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, -1000, 1.5)
    gyro_drive(0, -800, cm(50))

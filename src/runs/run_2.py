import time

from ..gsgr.config import cfg
from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.enums import Attachment, Pivot
import color as col
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, gyro_wall_align, hold_attachment, run_attachment

display_as = 2
color = col.YELLOW


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(
        0,
        900,
        impact(cm(30.72)),
        accelerate=10,
        decelerate=40,
    )
    run_attachment(Attachment.FRONT_LEFT, 600, 0.7, stall=True)
    time.sleep(0.1)
    gyro_drive(
        0,
        -1000,
        cm(43.2),
        accelerate=60,
        decelerate=0,
    )
    gyro_turn(100)

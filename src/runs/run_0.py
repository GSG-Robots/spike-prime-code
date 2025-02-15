import time

from gsgr.conditions import THEN, cm, deg, sec
from gsgr.correctors import accelerate_linar, speed
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    drive,
    free_attachment,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = 0
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    drive(accelerate_linar(speed(100, 100), cm(5)), sec(5))

import time

from gsgr.conditions import THEN, cm, deg, sec
from gsgr.correctors import speed
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

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 50, cm(50))
    time.sleep(1)
    gyro_drive(0, -50, cm(60))
    drive(speed(0, 50), sec(1))

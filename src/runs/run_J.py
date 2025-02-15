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

display_as = "J"
color = Color.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()

    run_attachment(1, 100, 0.5)
    run_attachment(2, 100, 0.5)
    run_attachment(3, 100, 0.5)
    run_attachment(4, 100, 0.5)

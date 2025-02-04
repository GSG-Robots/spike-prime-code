import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.correctors import speed
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    drive,
    gyro_turn,
    run_attachment,
    hold_attachment,
    free_attachment,
)

display_as = "J"
color = Color.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()

    run_attachment(1, 100, .5)
    run_attachment(2, 100, .5)
    run_attachment(3, 100, .5)
    run_attachment(4, 100, .5)

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

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 50, cm(50))
    time.sleep(1)
    gyro_drive(0, -50, cm(60))
    drive(speed(0, 50), sec(1))


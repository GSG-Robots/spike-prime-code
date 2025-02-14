import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.correctors import speed, accelerate_linar
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

display_as = 0
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    drive(accelerate_linar(speed(100, 100), cm(5)), sec(5))
    


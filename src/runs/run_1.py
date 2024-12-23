import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.enums import Color, Attachment
from gsgr.movement import gyro_set_origin, gyro_drive, gyro_turn, run_attachment, hold_attachment, free_attachment

display_as = 1
color = Color.GREEN


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 60, cm(100))

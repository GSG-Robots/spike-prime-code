import time

from gsgr.conditions import cm, impact, pickup, sec
from gsgr.enums import Color, Pivot, Attachment
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_drive, gyro_turn, run_attachment, hold_attachment

display_as = "T"
color = Color.GREEN


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 70, impact(cm(25), min=30), accelerate=5, decelerate=5)
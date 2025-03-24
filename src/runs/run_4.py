import time

from gsgr.conditions import OR, cm, impact, pickup, sec, impact
from gsgr.enums import Attachment, Color, Pivot
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, run_attachment

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 80, impact(cm(55)), accelerate=5, decelerate=5)
    gyro_drive(0, -100, pickup(impact(cm(70))), accelerate=5, decelerate=5)

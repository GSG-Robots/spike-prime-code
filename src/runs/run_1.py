import time

from gsgr.conditions import cm, sec
from gsgr.enums import Color, Pivot
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_drive, gyro_turn

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_drive(0, -30, sec(0.5))
    gyro_set_origin()

    gyro_drive(0, 50, cm(56), accelerate=10, decelerate=5)
    time.sleep(1)
    gyro_drive(0, -50, cm(59), accelerate=12)
    gyro_turn(-45, 150, Pivot.LEFT_WHEEL)

from gsgr.conditions import cm, sec
from gsgr.enums import Color
from gsgr.movement import (
    gyro_drive,
    gyro_turn,
    gyro_set_origin,
)
import time

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, -60, cm(50), decelerate=10)
    time.sleep(1)
    gyro_drive(0, 75, sec(5))
    gyro_turn(20, 150)

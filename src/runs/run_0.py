import time
import color as col
from ..gsgr.enums import Pivot

from ..gsgr.conditions import cm, sec
from ..gsgr.movement import (
    gyro_drive,
    gyro_turn,
    gyro_wall_align,
)

display_as = 0
color = col.RED


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(0, 600, cm(10), accelerate=10, decelerate=30)
    gyro_turn(90, pivot=Pivot.LEFT_WHEEL, timeout=2500)

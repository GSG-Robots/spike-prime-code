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
    gyro_wall_align(0.3)
    gyro_drive(0, 800, cm(20))
    gyro_turn(90, pivot=Pivot.CENTER)

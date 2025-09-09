import color as col

from ..gsgr.conditions import sec
from ..gsgr.movement import (
    gyro_drive,
    gyro_wall_align,
)

display_as = 0
color = col.RED


def run():
    # Set Gyro Origin
    gyro_wall_align(0.3)
    gyro_drive(0, 800, sec(5))

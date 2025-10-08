from ..gsgr.conditions import wheels_blocked
import color as col
from ..gsgr.enums import Pivot

from ..gsgr.conditions import OR, cm
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
)

display_as = 7
color = col.PURPLE


def run():
    # Set Gyro Origin
    gyro_wall_align(0.5)
    gyro_drive(0, 900, cm(10), accelerate=10, brake=False)
    gyro_turn(-37, pivot=Pivot.RIGHT_WHEEL, brake=False)
    gyro_drive(-37, 500, OR(cm(37), wheels_blocked()), decelerate=60)
    gyro_drive(-37, -1000, cm(15), accelerate=10)

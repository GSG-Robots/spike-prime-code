import color as col

from ..gsgr.conditions import cm
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
)

display_as = 7
color = col.PURPLE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 500, cm(48), accelerate=10, decelerate=30)
    gyro_drive(0, -700, cm(15), accelerate=10, decelerate=30)


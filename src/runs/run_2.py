from src.gsgr import interpolators
from ..gsgr.config import PID
from ..gsgr.conditions import cm, sec
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, gyro_wall_align

display_as = 2
color = Color.GREEN


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(
        0,
        40,
        cm(50),
        accelerate=10,
        decelerate=40,
    )

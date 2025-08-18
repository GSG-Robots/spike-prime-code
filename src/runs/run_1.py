from src.gsgr import interpolators
from ..gsgr.config import PID
from ..gsgr.conditions import cm, sec
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_wall_align

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(
        0,
        40,
        cm(50),
        accelerate=10,
        decelerate=40,
        pid=PID(0.9, 0.009, -0.9),
    )

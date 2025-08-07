from ..gsgr.conditions import cm
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    # gyro_drive(0, -30, sec(0.5))
    gyro_set_origin()

    # gyro_drive(0, 60, cm(20))
    gyro_turn(-45, 80, pivot=Pivot.RIGHT_WHEEL)

from ..gsgr.conditions import cm
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = 2
color = Color.GREEN


def run():
    # Set Gyro Origin
    # gyro_drive(0, -30, sec(0.5))
    gyro_set_origin()
    gyro_turn(-90, 50, pivot=Pivot.RIGHT_WHEEL)
    # for i in range(10):
    gyro_drive(-90, 40, cm(50), accelerate=10, decelerate=10)
        # gyro_turn(90, 70, pivot=Pivot.RIGHT_WHEEL)
        # gyro_drive(90, 40, cm(30), decelerate=10)
        # gyro_turn(-90, 70, pivot=Pivot.RIGHT_WHEEL)

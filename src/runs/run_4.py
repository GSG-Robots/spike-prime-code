from ..gsgr.conditions import cm
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn
import hub
display_as = 4
color = Color.BLUE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_turn(-90, 60, pivot=Pivot.RIGHT_WHEEL)
    for i in range(10):
        gyro_drive(-90, 80, cm(40), accelerate=10, decelerate=30)
        gyro_turn(90, 70, pivot=Pivot.RIGHT_WHEEL)
        gyro_drive(90, 80, cm(40), accelerate=10, decelerate=30)
        gyro_turn(-90, 70, pivot=Pivot.RIGHT_WHEEL)
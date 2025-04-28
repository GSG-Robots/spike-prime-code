from gsgr.conditions import cm, impact, pickup
from gsgr.enums import Color
from gsgr.movement import gyro_drive, gyro_set_origin

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 80, impact(cm(55)), accelerate=5, decelerate=5)
    gyro_drive(0, -100, pickup(impact(cm(70))), accelerate=5, decelerate=5)

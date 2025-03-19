from gsgr.conditions import cm
from gsgr.enums import Color, Pivot
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn
)

display_as = "N"
color = Color.ORANGE


def run():
    gyro_set_origin()
    # gyro_drive(-5, 65, cm(110))
    gyro_drive(0, 70, cm(70))
    gyro_turn(45, 90, Pivot.RIGHT_WHEEL)
    gyro_drive(45, 70, cm(20))
    gyro_turn(90, 90, Pivot.RIGHT_WHEEL)
    gyro_drive(90, 70, cm(50))
    gyro_turn(90, 90, Pivot.LEFT_WHEEL)
    

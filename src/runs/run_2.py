import time
from gsgr.conditions import cm, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
    Pivot
)

display_as = 2
color = Color.WHITE


# FEATURE FLAGS
# x Sekunden
FEATURE_KORALLEN = False
# #############


# Gesamt: x Sekunden
def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 70, cm(30), accelerate=5, decelerate=5)
    gyro_turn(-35, 90, Pivot.LEFT_WHEEL)
    gyro_drive(-35, 70, cm(20), accelerate=5, decelerate=5)
    run_attachment(Attachment.FRONT_LEFT, -100, 1.5, stall=True, untension=180)
    gyro_turn(-10, 90, Pivot.RIGHT_WHEEL)
    gyro_turn(-35, 90, Pivot.LEFT_WHEEL)
    gyro_drive(-35, 40, cm(3), accelerate=5, decelerate=5)
    run_attachment(Attachment.FRONT_RIGHT, -20, 4.5, stall=True)
    run_attachment(Attachment.FRONT_RIGHT, 80, 1, stall=True, untension=180)
    # gyro_turn(-25, 90, Pivot.LEFT_WHEEL)
    # gyro_turn(-35, 90, Pivot.RIGHT_WHEEL)
    gyro_drive(-35, -70, cm(22), accelerate=5, decelerate=5)
    gyro_turn(-125, 90, Pivot.LEFT_WHEEL)
    gyro_drive(-125, -30, cm(10), accelerate=5, decelerate=25)

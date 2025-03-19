import time

from gsgr.conditions import OR, cm, sec
from gsgr.enums import Attachment, Color, Pivot
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, run_attachment

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 60, cm(65), accelerate=5, decelerate=5)
    run_attachment(Attachment.BACK_RIGHT, -100, 2)
    run_attachment(Attachment.FRONT_RIGHT, -100, 4.5)
    gyro_drive(0, 60, cm(5), accelerate=5, decelerate=5)
    run_attachment(Attachment.FRONT_LEFT, -50, 2.5)
    gyro_drive(0, -60, cm(40), accelerate=5, decelerate=5)
    gyro_turn(-45, 100, Pivot.RIGHT_WHEEL)
    gyro_drive(-45, 40, OR(cm(35), sec(5)), accelerate=5, decelerate=15)
    gyro_drive(-45, -100, OR(cm(40), sec(10)), accelerate=5)
    
import time

from gsgr.conditions import cm, sec
from gsgr.enums import Color, Pivot, Attachment
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_drive, gyro_turn, run_attachment, hold_attachment

display_as = 0
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_drive(0, -35, sec(1), accelerate=10)
    gyro_set_origin()

    gyro_drive(0, 70, cm(66), accelerate=5, decelerate=5)
    gyro_turn(85, 95, Pivot.RIGHT_WHEEL)
    gyro_drive(85, 30, cm(10))
    gyro_drive(85, -30, cm(15))
    run_attachment(Attachment.FRONT_LEFT, 70, 1, stall=True)
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(85, -75, cm(75))
    run_attachment(Attachment.FRONT_RIGHT, -100, 6, stall=True)
    gyro_drive(85, -75, cm(37))
    gyro_turn(50, 90, Pivot.LEFT_WHEEL)
    gyro_drive(50, -75, cm(17))
    gyro_turn(30, 90, Pivot.LEFT_WHEEL)
    gyro_drive(30, -75, cm(60))

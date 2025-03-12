import time

from gsgr.conditions import cm, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, run_attachment

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, -60, cm(50), decelerate=10)
    time.sleep(1)
    run_attachment(Attachment.BACK_LEFT, -100, 5, stall=False, await_completion=False)
    gyro_drive(0, 75, sec(5))
    gyro_turn(20, 150)

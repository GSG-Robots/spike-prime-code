import time

from gsgr.conditions import cm, impact, pickup, sec
from gsgr.config import PID
from gsgr.enums import Attachment, Color, Pivot
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, hold_attachment, run_attachment

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    # gyro_drive(0, -30, sec(0.5))
    # gyro_set_origin()

    run_attachment(Attachment.FRONT_RIGHT, 100, 1)
    run_attachment(Attachment.FRONT_LEFT, 100, 1)
    run_attachment(Attachment.BACK_RIGHT, 100, 1)
    run_attachment(Attachment.BACK_LEFT, 100, 1)

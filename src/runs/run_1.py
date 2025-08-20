import time
from src.gsgr import interpolators
from ..gsgr.config import PID
from ..gsgr.conditions import cm, sec
from ..gsgr.enums import Attachment, Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_wall_align, run_attachment

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    # gyro_drive(
    #     0,
    #     60,
    #     cm(80),
    #     accelerate=10,
    #     decelerate=40,
    # )
    run_attachment(Attachment.FRONT_RIGHT, 100, 3)
    run_attachment(Attachment.BACK_RIGHT, 30, 1)
    # gyro_drive(
    #     0,
    #     -60,
    #     cm(80),
    #     accelerate=10,
    #     decelerate=40,
    # )

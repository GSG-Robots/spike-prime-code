import color as col
import time
from ..gsgr.conditions import cm, pickup, sec
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    run_attachment,
)

display_as = 5
color = col.GREEN


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(-1, 800, cm(40), accelerate=10, decelerate=30)
    gyro_turn(0)
    # run_attachment(Attachment.FRONT_RIGHT, 1000, 1.25)
    # gyro_turn(-6, 200, premature_ending_condition=sec(.5))
    gyro_drive(-1, 350, cm(8), accelerate=10, decelerate=30)
    gyro_drive(1, -800, cm(50))

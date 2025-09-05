import color as col

from ..gsgr.conditions import cm, pickup, sec
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    run_attachment,
    stop_attachment,
)

display_as = 4
color = col.GREEN


def run():
    # Set Gyro Origin

    # gyro_set_origin()
    # gyro_drive(-1, 700, cm(42), accelerate=10, decelerate=10)
    # gyro_drive(1, -400, cm(8), accelerate=10, decelerate=10)
    # gyro_turn(0)
    # gyro_drive(-1, 400, cm(12), accelerate=10, decelerate=30)
    # run_attachment(Attachment.FRONT_LEFT, 1000, 2)
    # run_attachment(Attachment.FRONT_RIGHT, -1000, .75)
    # gyro_drive(1, -1000, cm(50), accelerate=10, decelerate=0)
    
    gyro_set_origin()
    gyro_drive(-1, -700, cm(42), accelerate=10, decelerate=10)
    gyro_drive(1, 400, cm(8), accelerate=10, decelerate=10)
    gyro_turn(0)
    gyro_drive(1, -400, cm(14), accelerate=10, decelerate=30, brake=2)
    run_attachment(Attachment.BACK_RIGHT, 1000, await_completion=False)
    gyro_turn(-6, premature_ending_condition=sec(1.5))
    stop_attachment()
    run_attachment(Attachment.BACK_LEFT, -1000, 0.5)
    # gyro_drive(1, -1000, cm(1.5), accelerate=0, decelerate=0)
    gyro_drive(1, 1000, cm(50), accelerate=10, decelerate=0)

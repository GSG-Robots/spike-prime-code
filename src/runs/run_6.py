import color as col

from ..gsgr.conditions import cm, sec
from ..gsgr.config import PID, configure
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import (
    free_attachment,
    gyro_drive,
    gyro_turn,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
    stop_attachment,
)

display_as = 6
color = col.GREEN
# TODO: Remove custom PID values
config = configure().gyro_drive(PID(1.2, 0, -0.2))


def run():
    # Set Gyro Origin
    gyro_wall_align(0.5)
    run_attachment(Attachment.FRONT_LEFT, 100, stall=True, await_completion=False)
    gyro_drive(0, 800, cm(60), accelerate=10, decelerate=30)
    stop_attachment(Attachment.FRONT_LEFT)
    gyro_turn(-90, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(-90, 800, cm(44), accelerate=10, decelerate=30)
    gyro_turn(10, pivot=Pivot.RIGHT_WHEEL)
    gyro_turn(0, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(0, -600, cm(5), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 300, -400, stall=True, when_i_say_duration_i_mean_degrees=True)
    free_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(0, 600, cm(6), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 300, 250, stall=False, when_i_say_duration_i_mean_degrees=True)
    gyro_drive(0, 500, cm(4), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 300, 200, stall=True, when_i_say_duration_i_mean_degrees=True)
    gyro_drive(0, 500, cm(5), accelerate=10, decelerate=30)
    gyro_drive(0, 1000, sec(0.5), pid=PID(0, 0, 0))
    run_attachment(Attachment.FRONT_RIGHT, 1000, 5)
    run_attachment(Attachment.FRONT_RIGHT, -600, 1.3, stall=True)
    hold_attachment(Attachment.FRONT_LEFT)
    gyro_drive(-1, -500, cm(19), accelerate=10, decelerate=30)
    run_attachment(Attachment.BACK_RIGHT, 400, 2, stall=True)
    gyro_drive(0, 1000, cm(5))
    gyro_turn(90)
    gyro_drive(90, 1000, cm(25))
    gyro_turn(-20, 100, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(-20, -1000, cm(79))

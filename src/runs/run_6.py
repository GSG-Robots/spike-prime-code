import color as col

from ..gsgr.conditions import cm, sec
from ..gsgr.config import PID, configure
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, gyro_wall_align, hold_attachment, run_attachment

display_as = 6
color = col.GREEN
# TODO: Remove custom PID values
config = configure().gyro_drive(PID(1.2, 0, -0.2))


def run():
    # Set Gyro Origin
    gyro_wall_align(0.3)
    # run_attachment(Attachment.FRONT_LEFT, 100, stall=True, await_completion=False)
    gyro_drive(0, 800, cm(57.5), accelerate=10, decelerate=30)
    # stop_attachment(Attachment.FRONT_LEFT)
    gyro_turn(-90, pivot=Pivot.RIGHT_WHEEL)
    gyro_drive(-90, 800, cm(44), accelerate=10, decelerate=30)
    gyro_turn(10, pivot=Pivot.RIGHT_WHEEL, timeout=2500)
    gyro_turn(0, pivot=Pivot.RIGHT_WHEEL, timeout=1500)
    # gyro_drive(0, -600, cm(5), accelerate=10, decelerate=30)
    # run_attachment(Attachment.FRONT_LEFT, 300, -400, stall=True, when_i_say_duration_i_mean_degrees=True)
    # free_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(0, 700, cm(3), accelerate=10, decelerate=45)
    run_attachment(Attachment.FRONT_LEFT, 300, 250, stall=False, when_i_say_duration_i_mean_degrees=True)
    gyro_drive(0, 500, cm(3), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 300, 200, stall=True, when_i_say_duration_i_mean_degrees=True)
    gyro_drive(0, 700, cm(6), accelerate=10, decelerate=30)
    gyro_drive(0, 1000, sec(0.5), pid=PID(0, 0, 0))
    run_attachment(Attachment.FRONT_RIGHT, 1000, 5.25)
    run_attachment(Attachment.FRONT_RIGHT, -600, 1.3, stall=True)
    hold_attachment(Attachment.FRONT_LEFT)
    gyro_drive(0, -500, cm(15.5), accelerate=10, decelerate=30)
    run_attachment(Attachment.BACK_RIGHT, 400, 2, stall=True)
    gyro_drive(0, 1000, cm(5))
    gyro_turn(90)
    gyro_set_origin()
    gyro_drive(0, 1000, cm(25))
    gyro_turn(60, 120, pivot=Pivot.CENTER)
    gyro_drive(60, 1000, cm(79))

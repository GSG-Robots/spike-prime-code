import color as col

from ..gsgr.conditions import cm, sec
from ..gsgr.config import PID, configure
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    gyro_drive,
    gyro_turn,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
)

display_as = 6
color = col.GREEN
config = configure().gyro_drive(PID(1.2, 0, -0.2))


def run():
    # Set Gyro Origin
    gyro_wall_align(0.2)
    gyro_drive(0, 700, cm(67), accelerate=10, decelerate=30)
    gyro_turn(-90)
    gyro_drive(-90, 700, cm(34.5), accelerate=10, decelerate=30)
    gyro_turn(0)
    gyro_drive(0, -500, cm(11), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, -200, 1.5, stall=True)
    gyro_drive(0, 500, cm(4.2), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 250, 1, stall=True)
    gyro_drive(0, 500, cm(4), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, 300, 1, stall=True)
    gyro_drive(0, 500, cm(5), accelerate=10, decelerate=30)
    gyro_drive(0, 1000, sec(0.5), pid=PID(0, 0, 0))
    run_attachment(Attachment.FRONT_RIGHT, 1000, 5)
    run_attachment(Attachment.FRONT_RIGHT, -600, 1.3, stall=True)
    hold_attachment(Attachment.FRONT_LEFT)
    gyro_drive(0, -500, cm(16.5), accelerate=10, decelerate=30)
    run_attachment(Attachment.BACK_RIGHT, 600, 1.3, stall=True)
    gyro_drive(0, 800, cm(3.5))
    gyro_turn(90)
    gyro_drive(90, 800, cm(30))
    gyro_turn(0)
    gyro_drive(0, -800, cm(79))

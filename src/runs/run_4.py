import color as col

from ..gsgr.conditions import cm, pickup
from ..gsgr.enums import Attachment
from ..gsgr.movement import gyro_drive, gyro_turn, gyro_wall_align, run_attachment

display_as = 4
color = col.GREEN


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(0, 500, cm(52.5), accelerate=10, decelerate=30)
    gyro_turn(5)
    gyro_drive(5, 500, cm(19), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_LEFT, -1000, 1.3, stall=True)
    gyro_drive(0, -400, cm(4), accelerate=10, decelerate=0)
    run_attachment(Attachment.FRONT_RIGHT, -1000, 0.9, stall=True)
    gyro_drive(0, -400, cm(1), accelerate=10, decelerate=0)
    run_attachment(Attachment.BACK_LEFT, -700, 2, stall=True, untension=5)
    gyro_drive(5, -900, cm(30), accelerate=10, decelerate=0)
    gyro_drive(0, -900, pickup(cm(70)), accelerate=10, decelerate=0)

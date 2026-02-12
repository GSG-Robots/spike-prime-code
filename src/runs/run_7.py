import color as col

from ..gsgr.conditions import OR, cm, wheels_blocked
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import gyro_drive, gyro_turn, gyro_wall_align, run_attachment

display_as = 7
color = col.PURPLE


def run():
    # Set Gyro Origin
    gyro_wall_align(0.3)
    gyro_drive(0, 900, cm(10), accelerate=10, brake=False)
    gyro_turn(-37, pivot=Pivot.RIGHT_WHEEL, brake=False)
    gyro_drive(-37, 500, OR(cm(34), wheels_blocked()), decelerate=60)
    run_attachment(Attachment.FRONT_RIGHT, -1000, 1)
    gyro_drive(-37, -1000, cm(70), accelerate=10)

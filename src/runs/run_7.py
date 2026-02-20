import color as col

from ..gsgr.conditions import OR, cm, wheels_blocked
from ..gsgr.enums import Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = 7
color = col.PURPLE


def run():
    gyro_set_origin()
    gyro_drive(0, 900, cm(13), accelerate=10, brake=False)
    gyro_turn(-37, pivot=Pivot.RIGHT_WHEEL, brake=False)
    gyro_drive(-37, 1000, OR(cm(29), wheels_blocked()), decelerate=60)
    # run_attachment(Attachment.FRONT_RIGHT, -1000, 1)
    gyro_drive(-37, -1000, cm(50), accelerate=10)

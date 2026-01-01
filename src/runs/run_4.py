import time

import color as col

from ..gsgr.conditions import OR, cm, impact, pickup, wheels_blocked
from ..gsgr.config import PID, configure
from ..gsgr.enums import Attachment
from ..gsgr.movement import (
    free_attachments,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    run_attachment,
    stop_attachment,
)

display_as = 4
color = col.GREEN
config = configure()


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(0, 700, OR(cm(71), wheels_blocked()), decelerate=13)
    run_attachment(Attachment.FRONT_RIGHT, -250, 2, untension=10)
    run_attachment(Attachment.FRONT_LEFT, 700, 0.5, untension=5)
    gyro_drive(0, -500, cm(9))
    gyro_drive(0, 200, cm(3))
    run_attachment(Attachment.BACK_LEFT, 700, 0.9, untension=5)
    gyro_drive(0, -500, OR(cm(20), pickup(impact(wheels_blocked()))), brake=False)
    gyro_drive(0, -1000, OR(cm(50), pickup(impact(wheels_blocked()))), decelerate=13)

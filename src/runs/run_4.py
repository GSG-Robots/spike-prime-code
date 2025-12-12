import time
import color as col

from ..gsgr.conditions import cm, pickup, wheels_blocked, OR, impact
from ..gsgr.enums import Attachment
from ..gsgr.movement import free_attachments, gyro_drive, gyro_turn, gyro_wall_align, run_attachment, stop_attachment
from ..gsgr.config import configure

display_as = 4
color = col.GREEN
config = configure()


def run():
    # Set Gyro Origin
    gyro_wall_align()
    gyro_drive(0, 700, OR(cm(71), wheels_blocked()), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_RIGHT, -350, 1.6, untension=10)
    run_attachment(Attachment.FRONT_LEFT, 700, 0.5, untension=5)
    gyro_drive(0, -700, cm(9), accelerate=10, decelerate=30)
    gyro_drive(0, 200, cm(4), accelerate=10, decelerate=30)
    run_attachment(Attachment.BACK_LEFT, -700, 1.75, untension=5)
    gyro_drive(0, -1000, OR(cm(70), pickup(impact(wheels_blocked()))), accelerate=10, decelerate=30)

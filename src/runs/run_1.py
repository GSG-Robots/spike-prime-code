from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.enums import Attachment
import color as col
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_wall_align, hold_attachment, run_attachment

display_as = 1
color = col.RED


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    gyro_set_origin()
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(
        0,
        900,
        impact(cm(86.4)),
        accelerate=10,
        decelerate=20,
    )
    run_attachment(Attachment.FRONT_RIGHT, 1000, 0.9, untension=25, stall=True)
    gyro_drive(
        0,
        -1000,
        pickup(cm(96)),
        accelerate=10,
        decelerate=40,
    )

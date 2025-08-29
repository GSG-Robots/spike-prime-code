from ..gsgr.conditions import cm, impact, pickup, sec
from ..gsgr.enums import Attachment
import color as col
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_wall_align, hold_attachment, run_attachment

display_as = 0
color = col.GREEN


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    gyro_set_origin()
    gyro_drive(
        0,
        30,
        sec(10),
        accelerate=10,
        decelerate=20,
    )

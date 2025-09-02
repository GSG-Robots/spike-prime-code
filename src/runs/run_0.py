from src.gsgr.config import cfg
from src.gsgr.interpolators import linear
from ..gsgr.conditions import cm, impact, pickup, sec
from ..gsgr.enums import Attachment, Pivot
import color as col
from ..gsgr.movement import (
    free_attachments,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
)

display_as = 0
color = col.GREEN
import motor


def run():
    # Set Gyro Origin
    # gyro_wall_align()
    gyro_set_origin()
    gyro_drive(
        0,
        700,
        cm(30),
        accelerate=10,
        decelerate=30,
    )
    # for i in range(5):
    #     print(1)
    #     gyro_turn(90, pivot=Pivot.RIGHT_WHEEL)
    #     print(2)
    #     gyro_drive(
    #         90,
    #         700,
    #         cm(30),
    #         accelerate=10,
    #         decelerate=30,
    #     )
    #     gyro_turn(-90, pivot=Pivot.RIGHT_WHEEL)
    #     gyro_drive(
    #         -90,
    #         700,
    #         cm(30),
    #         accelerate=10,
    #         decelerate=30,
    #     )
    # free_attachments()

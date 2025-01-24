import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    gyro_turn,
    run_attachment,
    hold_attachment,
    free_attachment,
)

display_as = 1
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(1, 50, cm(49), p_correction=0.5)
    run_attachment(Attachment.BACK_LEFT, 100, 2, False, True)
    run_attachment(Attachment.FRONT_RIGHT, 100, 4)


# gyro_drive(0, -40, cm(70))

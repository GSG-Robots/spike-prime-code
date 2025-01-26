import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.correctors import speed
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    drive,
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

    gyro_drive(
        0,
        50,
        cm(51),
        p_correction=1.4,
        i_correction=0,
        d_correction=-0.7,
    )
    run_attachment(Attachment.BACK_LEFT, 100, 2)
    run_attachment(Attachment.BACK_LEFT, -30, 1)
    # gyro_drive(0, -50, cm(1), p_correction=0, i_correction=0, d_correction=0)
    drive(speed(-50), cm(1))
    run_attachment(Attachment.FRONT_RIGHT, -100, 3, False, True)
    gyro_turn(-100, 50, sec(0.2))
    run_attachment(Attachment.FRONT_LEFT, 50, 1)
    gyro_turn(35, 50)
    gyro_drive(45, -100, cm(20))
    gyro_drive(0, -100, cm(50))


# gyro_drive(0, -40, cm(70))

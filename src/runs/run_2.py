import time
from gsgr.conditions import sec, deg, cm, OR
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    gyro_turn,
    run_attachment,
    hold_attachment,
    free_attachment,
)

display_as = 2
color = Color.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    
    run_attachment(Attachment.FRONT_RIGHT, 100, 1)
    run_attachment(Attachment.FRONT_RIGHT, -30, 1)
    free_attachment(Attachment.FRONT_RIGHT)

    gyro_drive(0, 65, cm(12))

    run_attachment(Attachment.FRONT_LEFT, 80, 1)

    gyro_turn(45, 50)
    gyro_drive(45, 75, cm(22))

    gyro_turn(0, 50)
    gyro_drive(0, 75, cm(15))

    run_attachment(Attachment.BACK_RIGHT, 100, 3.5)
    run_attachment(Attachment.BACK_RIGHT, -100, 1.5)

    gyro_drive(5, 20, cm(10))

    run_attachment(Attachment.FRONT_RIGHT, 80, 1.5)
    gyro_drive(5, 20, cm(1))
    run_attachment(Attachment.FRONT_RIGHT, -100, 1.2)

    run_attachment(Attachment.FRONT_LEFT, -80, 1.5)

    gyro_drive(0, -75, cm(5))
    gyro_turn(45, 70, OR(deg(45), sec(2)))
    gyro_drive(45, -100, cm(35))
    gyro_turn(20, 70, OR(deg(0), sec(2)))
    gyro_drive(20, -100, cm(45))

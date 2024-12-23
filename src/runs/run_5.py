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
from gsgr.configuration import config as cnf

display_as = 5
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 75, cm(20), accelerate_for=cm(10))

    gyro_turn(-45, 50)
    gyro_drive(-45, 75, cm(15))

    gyro_turn(0, 50)
    gyro_drive(0, 60, cm(22))

    gyro_turn(45, 50, THEN(deg(45), sec(1)))
    gyro_drive(45, 60, cm(20), decelerate_from=cm(10), decelerate_for=cm(13))

    run_attachment(Attachment.FRONT_RIGHT, -30, 1.5, True)
    run_attachment(Attachment.FRONT_RIGHT, 30, 1, True)
    run_attachment(Attachment.FRONT_RIGHT, -30, 1, True)
    run_attachment(Attachment.FRONT_RIGHT, 30, 1, True)
    free_attachment(Attachment.FRONT_RIGHT)

    gyro_drive(45, -50, cm(15))

    gyro_turn(87, 20, THEN(deg(87), sec(1)))
    gyro_drive(87, -50, cm(20))

    run_attachment(Attachment.FRONT_LEFT, 100, 4, True)

    gyro_drive(87, -50, cm(20))

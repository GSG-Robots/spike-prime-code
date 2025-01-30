import time
from gsgr.conditions import sec, deg, cm, THEN, OR
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

    gyro_drive(0, 75, cm(19), accelerate_for=cm(10))

    gyro_turn(-45, 50)
    gyro_drive(-45, 75, cm(16.5))

    gyro_turn(0, 50, p_correction=1.5)
    gyro_drive(0, 61, cm(21.5))

    gyro_turn(42, 50, THEN(deg(42), sec(1)))
    gyro_drive(
        43, 50, OR(cm(20), sec(2)), decelerate_from=cm(10), decelerate_for=cm(13)
    )

    run_attachment(Attachment.FRONT_RIGHT, -100, 2, False, True)
    run_attachment(Attachment.FRONT_RIGHT, 100, 1.75, False, True)
    # run_attachment(Attachment.FRONT_RIGHT, 50, 1, True)
    # run_attachment(Attachment.FRONT_RIGHT, -30, 1, True)
    # run_attachment(Attachment.FRONT_RIGHT, 30, 1, True)
    # free_attachment(Attachment.FRONT_RIGHT)

    gyro_set_origin()
    gyro_drive(1, -50, cm(15.5))

    gyro_turn(46, 50, OR(deg(44), sec(1.6)))
    gyro_drive(45, -50, cm(21))
    run_attachment(Attachment.FRONT_LEFT, -100, 5.5, True)
    run_attachment(Attachment.FRONT_LEFT, 100, 0.2, True)
    gyro_drive(45, -70, cm(20))
    run_attachment(Attachment.FRONT_LEFT, 100, 1.5, True, untension=True)

    gyro_turn(90, 25)
    gyro_drive(90, -35, sec(2))
    gyro_drive(90, 35, cm(0.25))
    run_attachment(Attachment.BACK_LEFT, -70, 1.5)
    gyro_drive(90, 50, cm(18))

    gyro_drive(45, -50, cm(9))
    gyro_turn(176, 50, deg(176), accelerate_for=deg(150))
    time.sleep(0.5)
    gyro_set_origin()
    # gyro_turn(10, 50, deg(10))
    gyro_drive(0, 50, cm(15.5))
    gyro_turn(15, 50, deg(14))
    gyro_drive(14, 50, cm(8))

    # run_attachment(Attachment.BACK_RIGHT, -30, 1)

    # gyro_turn(35, 50)
    # gyro_drive(35, -70, cm(10))
    # gyro_turn(5, 40)

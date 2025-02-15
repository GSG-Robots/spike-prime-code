import time

from gsgr.conditions import OR, THEN, cm, deg, sec
from gsgr.configuration import config as cnf
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    free_attachment,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    run_attachment,
    stop_attachment,
)

display_as = 5
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    # Zum Wal
    gyro_drive(0, 75, cm(18), accelerate_for=cm(10))

    gyro_turn(-45, 50)
    gyro_drive(-45, 75, cm(16.5))

    gyro_turn(0, 50, p_correction=1.5)
    gyro_drive(0, 61, cm(22.5))

    gyro_turn(41, 50, THEN(deg(41), sec(0.5)))
    gyro_drive(
        41, 50, OR(cm(20), sec(3)), decelerate_from=cm(10), decelerate_for=cm(13)
    )

    # Wal füllen
    run_attachment(Attachment.FRONT_RIGHT, -100, 2, False, True)
    run_attachment(Attachment.FRONT_RIGHT, 100, 1.75, False, True)

    # Fahrt zu Walen
    gyro_set_origin()
    gyro_drive(0, -50, cm(12))

    gyro_turn(46, 50, OR(deg(44), sec(1.6)))
    gyro_drive(45, -50, cm(24))

    # Wale aufdecken
    run_attachment(Attachment.FRONT_LEFT, -100, 5.5, True)
    run_attachment(Attachment.FRONT_LEFT, 100, 0.2, True)
    gyro_drive(45, -70, cm(20))
    run_attachment(Attachment.FRONT_LEFT, 100, stop_on_resistance=True, untension=True)

    # Zum U-Boot
    gyro_turn(85, 25)
    gyro_drive(85, -35, sec(2))
    gyro_drive(85, 35, cm(0.25))
    stop_attachment()
    run_attachment(Attachment.FRONT_LEFT, -80, 0.3)
    # U-boot nach drüben
    run_attachment(Attachment.BACK_LEFT, -70, 1.5)
    gyro_drive(85, 50, cm(18))

    gyro_drive(45, -50, cm(9))
    gyro_turn(176, 50, deg(176), accelerate_for=deg(150))
    time.sleep(0.5)
    gyro_set_origin()
    # Hebel umfahren
    gyro_drive(0, 50, cm(15.5))
    gyro_turn(15, 50, OR(deg(14), sec(2.5)))
    gyro_drive(14, 50, cm(8))
    gyro_set_origin()
    gyro_turn(15, 50, OR(deg(15), sec(2.5)))
    gyro_drive(15, -50, cm(7.5))
    gyro_turn(95, 50, OR(deg(95), sec(2.5)))

    # run_attachment(Attachment.BACK_RIGHT, -30, 1)

    # gyro_turn(35, 50)
    # gyro_drive(35, -70, cm(10))
    # gyro_turn(5, 40)

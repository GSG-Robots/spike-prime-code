import time
from gsgr.conditions import sec, deg, cm, THEN, line
from gsgr.correctors import speed
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    gyro_turn,
    run_attachment,
    hold_attachment,
    free_attachment,
    drive,
)
from gsgr.configuration import config as cnf

display_as = 3
color = Color.BLUE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    run_attachment(Attachment.FRONT_LEFT, -20, 1)

    # Zum Boot fahren
    gyro_drive(0, 40, cm(20), accelerate_for=cm(10))
    # Boot nach vorne schieben
    gyro_drive(0, 70, cm(75), accelerate_for=cm(10))

    drive(speed(0, -50), sec(1))
    drive(speed(0, 50), sec(1))

    # Turm aufstellen
    run_attachment(Attachment.FRONT_LEFT, 50, 0.5)
    for _ in range(8):
        run_attachment(Attachment.FRONT_LEFT, 50, 0.2)
        gyro_drive(0, -25, cm(1))

    time.sleep(0.5)

    # In die andere Base fahren
    gyro_drive(0, -90, cm(21))
    gyro_turn(-40, 70)
    gyro_drive(-40, 70, cm(35))
    gyro_turn(-12, 45)
    gyro_drive(-12, 70, cm(40))
    gyro_turn(5, 70)
    gyro_drive(5, 100, cm(70))

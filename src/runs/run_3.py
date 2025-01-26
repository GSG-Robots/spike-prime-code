import time
from gsgr.conditions import sec, deg, cm, THEN, line
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

display_as = 3
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 40, cm(15))

    # time.sleep(0.3)

    gyro_drive(0, 70, cm(80), p_correction=1.7, d_correction=-0.7) # cm(80),

    for _ in range(10):
        gyro_drive(0, -10, cm(1))

        run_attachment(Attachment.FRONT_LEFT, 50, 0.2)

    time.sleep(.5)

    gyro_drive(0, -90, cm(25))
    
    # Zurück nach Hause
    gyro_turn(-50, 70)
    gyro_drive(-50, 70, cm(30))    
    gyro_turn(-10, 70)
    gyro_drive(-10, 70, cm(30))
    gyro_turn(15, 70)
    gyro_drive(15, 100, cm(40))

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

display_as = 3
color = Color.YELLOW


def run():
    # Set Gyro Origin
    gyro_set_origin()

    run_attachment(Attachment.FRONT_RIGHT, -50, 1)
    free_attachment(Attachment.FRONT_RIGHT)

    gyro_drive(0, 40, cm(15))

    # time.sleep(0.3)

    gyro_drive(0, 70, cm(80), i_correction=3, accelerate_for=cm(10))
    
    gyro_drive(0, 40, cm(10), i_correction=3)

    # gyro_turn(0, 20)

    run_attachment(Attachment.FRONT_LEFT, 15, 2)

    for _ in range(8):
        gyro_drive(0, -10, cm(1))

        run_attachment(Attachment.FRONT_LEFT, 50, 0.2)

    time.sleep(.5)

    run_attachment(Attachment.FRONT_RIGHT, 100, 2.5)

    gyro_turn(-90, 45)

    gyro_drive(-90, -90, cm(10))

    gyro_drive(-90, 50, cm(20))
    
    gyro_turn(0, 45)
    
    gyro_drive(0, 50, cm(30))
    gyro_drive(0, 100, cm(50))

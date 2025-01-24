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
    run_attachment(Attachment.FRONT_RIGHT, 100, 1.3, True, False)
    # run_attachment(Attachment.FRONT_RIGHT, -30, 1, False, True)
    run_attachment(Attachment.FRONT_LEFT, 75, 1, True, True)
   # free_attachment(Attachment.FRONT_RIGHT)

    gyro_drive(0, 90, cm(10))

    gyro_turn(50, 60)
    gyro_drive(50, 80, cm(22))

    gyro_turn(0, 50)
    gyro_drive(0, 75, cm(20))

    run_attachment(Attachment.BACK_RIGHT, 100, 3.5, True, False)
    run_attachment(Attachment.BACK_RIGHT, -100, 1.5, False, True)

    gyro_drive(2, 30, cm(9))

    run_attachment(Attachment.FRONT_RIGHT, 100, 1.8, True, False)
    gyro_drive(0, 20, cm(1))
    run_attachment(Attachment.FRONT_RIGHT, 100, .8, True, False)
    run_attachment(Attachment.FRONT_RIGHT, -100, 1.2, True, True)
    
    gyro_drive(0, -10, cm(5))

    run_attachment(Attachment.FRONT_LEFT, -80, 1.5, True, False)

    gyro_drive(0, -75, cm(5))
    gyro_turn(35, 50, OR(deg(35), sec(2))) 
    gyro_drive(45, -100, cm(60))
    # gyro_turn(20, 70, OR(deg(0), sec(2)))
    # gyro_drive(20, -100, cm(45))

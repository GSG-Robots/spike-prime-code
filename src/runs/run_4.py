import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.enums import Color, Attachment
from gsgr.movement import gyro_set_origin, gyro_drive, gyro_turn, run_attachment, hold_attachment, free_attachment
from gsgr.configuration import config as cnf

display_as = 4
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    gyro_drive(0, 50, cm(5))

    run_attachment(Attachment.FRONT_RIGHT, -80, 1, stop_on_resistance=True, untension=True)

    run_attachment(Attachment.FRONT_RIGHT, 20, 2, stop_on_resistance=True, untension=True)

    gyro_drive(0, 50, cm(40))#, accelerate_for=cm(10))

    run_attachment(Attachment.FRONT_RIGHT, -30, 1.5, stop_on_resistance=0)

    gyro_drive(0, -50, cm(60), p_correction=0.3)#, accelerate_for=cm(10), decelerate_from=cm(50), decelerate_for=cm(10))

    free_attachment(Attachment.FRONT_RIGHT)

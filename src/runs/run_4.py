import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.enums import Color, Attachment
from gsgr.movement import gyro_set_origin, gyro_drive, gyro_turn, run_attachment, hold_attachment, run_attachment_degrees, free_attachment

display_as = 4
color = Color.RED


def run():
    gyro_set_origin()

    run_attachment(Attachment.FRONT_RIGHT, 50, 0.75)
    free_attachment(Attachment.FRONT_RIGHT)
    hold_attachment(Attachment.FRONT_RIGHT)
    
    gyro_drive(0, 50, cm(45), accelerate_for=1)
    run_attachment(Attachment.FRONT_RIGHT, -50, 1)
    gyro_drive(0, -50, cm(50), accelerate_for=1)


import time

from gsgr.conditions import OR, THEN, cm, deg, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    free_attachment,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = "N"
color = Color.ORANGE


def run():
    gyro_set_origin()
    gyro_drive(-5, 65, cm(110))

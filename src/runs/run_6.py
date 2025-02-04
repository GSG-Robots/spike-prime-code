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

display_as = "N"
color = "orange"


def run():
    gyro_set_origin()
    gyro_drive(-5, 65, cm(110))

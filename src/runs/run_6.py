import time

from gsgr.conditions import OR, THEN, cm, deg, sec
from gsgr.configuration import config as cnf
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
color = "orange"


def run():
    gyro_set_origin()
    gyro_drive(-5, 65, cm(110))

from gsgr.conditions import cm
from gsgr.enums import Color
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
)

display_as = "N"
color = Color.ORANGE


def run():
    gyro_set_origin()
    gyro_drive(-5, 65, cm(110))

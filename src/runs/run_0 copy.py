import time

from gsgr.config import cfg
import hub
from gsgr.conditions import THEN, cm, deg, sec
from gsgr.correctors import accelerate_linar, speed
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    Pivot,
    drive,
    free_attachment,
    gyro_drive,
    gyro_drive2,
    gyro_set_origin,
    gyro_speed_turn,
    gyro_turn,
    hold_attachment,
    run_attachment,
)
import hub

display_as = 9
color = Color.PINK


def wait_for_press():
    hub.button.left.was_pressed()

    while not hub.button.left.was_pressed():
        pass


def run():
    # Set Gyro Origin
    gyro_set_origin()
    
    hub.led(5)
    wait_for_press()
    hub.led(9)
    
    gyro_drive2(0, 45, cm(100))

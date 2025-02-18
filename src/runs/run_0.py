import time

import hub
from gsgr.conditions import THEN, cm, deg, sec
from gsgr.correctors import accelerate_linar, speed
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    drive,
    free_attachment,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = 0
color = Color.YELLOW


def wait_for_press():
    hub.button.left.was_pressed()

    while not hub.button.left.was_pressed():
        pass


def run():
    # Set Gyro Origin

    hub.led(5)
    wait_for_press()
    hub.led(9)
    gyro_set_origin()

    pair = hub.port.F.motor.pair(hub.port.E.motor)

    while not 89 < hub.motion.yaw_pitch_roll()[0] < 91:
        pair.run_at_speed(-20, -20)
    pair.hold()

    hub.led(5)
    wait_for_press()
    hub.led(9)

    while not -1 < hub.motion.yaw_pitch_roll()[0] < 1:
        pair.run_at_speed(20, 20)

    pair.hold()

    hub.led(5)
    wait_for_press()
    hub.led(9)
    gyro_turn(90, 50, gyro_tolerance=0)
    hub.led(5)
    wait_for_press()
    hub.led(9)
    gyro_turn(0, 50, gyro_tolerance=0)

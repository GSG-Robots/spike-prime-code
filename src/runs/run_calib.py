import hub

from ..gsgr.conditions import cm
from ..gsgr.enums import Pivot
import color as col
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = "3x3h"
color = col.RED


def run():
    # Set Gyro Origin
    hub.motion.yaw_pitch_roll(0)
    hub.button.center.was_pressed()
    while not hub.button.center.was_pressed():
        pass
    print(hub.motion.yaw_pitch_roll()[0])

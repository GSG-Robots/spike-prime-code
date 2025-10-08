import hub

from ..gsgr.conditions import cm
from ..gsgr.enums import Pivot
import color as col
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = "3x3h"
color = col.RED


def run():
    # Set Gyro Origin
    hub.motion_sensor.reset_yaw(0)
    while not hub.button.pressed(hub.button.POWER):
        pass
    print(hub.motion_sensor.tilt_angles()[0])

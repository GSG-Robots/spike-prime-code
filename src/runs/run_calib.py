import color as col
import hub

display_as = "3x3h"
color = col.RED


def run():
    # Set Gyro Origin
    hub.motion_sensor.reset_yaw(0)
    while not hub.button.pressed(hub.button.POWER):
        pass
    print(hub.motion_sensor.tilt_angles()[0])

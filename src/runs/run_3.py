from ..gsgr.conditions import cm
from ..gsgr.enums import Color, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn
import hub
display_as = 3
color = Color.RED


def run():
    # Set Gyro Origin
    hub.motion.yaw_pitch_roll(0)
    hub.button.center.was_pressed()
    while not hub.button.center.was_pressed():
        pass
    print(hub.motion.yaw_pitch_roll()[0])
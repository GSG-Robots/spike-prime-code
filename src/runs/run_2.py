from gsgr.conditions import Sec
from gsgr.movement import gyro_drive


metadata = {"display_as": 2, "color": "green"}
config = {}


def run():
    gyro_drive(80, 0, Sec(10), accelerate_for=5, decelerate_for=5)

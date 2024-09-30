from gsgr.conditions import Sec
from gsgr.movement import gyro_drive
from gsgr.configuration import config as cnfg


metadata = {"display_as": 2, "color": "green"}
config = {}


def run():
    print(cnfg.debug_mode)
    gyro_drive(80, 0, Sec(10), accelerate_for=5, decelerate_for=5)

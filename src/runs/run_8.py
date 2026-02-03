import time
import color as col
import hub
import motor_pair
import random

from ..gsgr.config import cfg
from ..gsgr.conditions import OR, cm, wheels_blocked
from ..gsgr.enums import Pivot, Attachment
from ..gsgr.movement import gyro_drive, gyro_turn, gyro_set_origin, run_attachment

display_as = 8
color = col.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 800, cm(80), accelerate=10, decelerate=10)
    gyro_turn(64, 120, Pivot.LEFT_WHEEL)
    gyro_drive(64, 800, cm(70), accelerate=10, decelerate=10)
    run_attachment(Attachment.FRONT_RIGHT, 200, 2)
    gyro_drive(64, -800, cm(70), accelerate=10, decelerate=10)
    gyro_turn(130, 120, Pivot.LEFT_WHEEL)
    run_attachment(Attachment.FRONT_RIGHT, -200, 3)
    run_attachment(Attachment.FRONT_RIGHT, 700, 3)
    gyro_drive(130, -800, cm(5), accelerate=10, decelerate=10)
    # motor_pair.move_tank(cfg.DRIVING_MOTORS, -1000, 1000)
    # while not hub.button.pressed(hub.button.POWER):
    #     time.sleep(10)
    #     if random.randint(0, 1):
    #         motor_pair.move_tank(cfg.DRIVING_MOTORS, 1000, -1000)
    #     else:
    #         motor_pair.move_tank(cfg.DRIVING_MOTORS, -1000, 1000)

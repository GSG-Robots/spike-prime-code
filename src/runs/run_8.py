import color as col

from ..gsgr.conditions import cm
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn, run_attachment

display_as = 8
color = col.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 1000, cm(76), accelerate=10, decelerate=10)
    gyro_turn(64, 120, Pivot.LEFT_WHEEL)
    gyro_drive(64, 1000, cm(50), accelerate=10, brake=69.42)
    gyro_drive(64, 500, cm(20), accelerate=10, decelerate=30)
    run_attachment(Attachment.FRONT_RIGHT, 200, 2)
    gyro_drive(64, -800, cm(70), accelerate=10, decelerate=10)
    gyro_turn(150, 120, Pivot.LEFT_WHEEL)
    run_attachment(Attachment.FRONT_RIGHT, -200, 1.5)
    run_attachment(Attachment.FRONT_RIGHT, 700, 1)
    gyro_drive(130, -800, cm(5), accelerate=10, decelerate=10)
    # motor_pair.move_tank(cfg.DRIVING_MOTORS, -1000, 1000)
    # while not hub.button.pressed(hub.button.POWER):
    #     time.sleep(10)
    #     if random.randint(0, 1):
    #         motor_pair.move_tank(cfg.DRIVING_MOTORS, 1000, -1000)
    #     else:
    #         motor_pair.move_tank(cfg.DRIVING_MOTORS, -1000, 1000


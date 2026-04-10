import color as col

from ..gsgr.conditions import THEN, cm, debug_cond, light_left_red
from ..gsgr.enums import Sensor
from ..gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = 5
color = col.GREEN
left_sensor = Sensor.LIGHT


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(
        -1,
        800,
        THEN(THEN(cm(2), debug_cond(light_left_red(600, below=True), col.RED)), cm(20)),
        accelerate=10,
        decelerate=50,
    )
    gyro_turn(0)
    # run_attachment(Attachment.FRONT_RIGHT, 1000, 1.25)
    # gyro_turn(-6, 200, premature_ending_condition=sec(.5))
    gyro_drive(-1, 350, cm(8), accelerate=10, decelerate=30)
    gyro_drive(-1, -800, cm(50))

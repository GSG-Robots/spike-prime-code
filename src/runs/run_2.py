from gsgr.conditions import Sec
from gsgr.enums import Color
from gsgr.movement import gyro_drive, gyro_turn, gyro_set_origin


display_as = 2
color = Color.GREEN


def run():
    gyro_set_origin()
    gyro_drive(80, 0, Sec(10), accelerate_for=5, decelerate_for=5)
    gyro_turn(180, p_correction=0.5, i_correction=0, d_correction=0)
    gyro_drive(80, 180, Sec(10), accelerate_for=5, decelerate_for=5)
    gyro_turn(180, p_correction=0.5, i_correction=0, d_correction=0)

import time
from gsgr.conditions import sec
from gsgr.correctors import speed, gyro_turn_pid
from gsgr.enums import Color
from gsgr.movement import drive, gyro_drive, gyro_set_origin, gyro_turn

display_as = 2
color = Color.GREEN


def run():
    gyro_set_origin()
    drive(gyro_turn_pid(0, speed(100)), sec(3))
    # gyro_drive(80, 0, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(180, p_correction=0.5, i_correction=0, d_correction=0)
    # gyro_drive(80, 180, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(0, p_correction=0.5, i_correction=0, d_correction=0)

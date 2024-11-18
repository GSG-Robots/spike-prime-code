import time
from gsgr.conditions import sec, deg
from gsgr.correctors import speed, gyro_drive_pid, gyro_turn_pid
from gsgr.enums import Color
from gsgr.movement import drive, gyro_set_origin

display_as = 2
color = Color.GREEN


def run():
    gyro_set_origin()
    # drive(gyro_drive_pid(0, speed(100)), sec(3))
    drive(gyro_drive_pid(0, speed(60)), sec(1))
    drive(gyro_turn_pid(90, speed(60)), deg(90))
    drive(gyro_drive_pid(90, speed(60)), sec(1))
    # drive(gyro_drive_pid(90, speed(100)), sec(3))
    # gyro_drive(80, 0, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(180, p_correction=0.5, i_correction=0, d_correction=0)
    # gyro_drive(80, 180, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(0, p_correction=0.5, i_correction=0, d_correction=0)

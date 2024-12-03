import time
from gsgr.conditions import sec, deg, cm, THEN
from gsgr.correctors import speed, gyro_drive_pid, gyro_turn_pid
from gsgr.enums import Color
from gsgr.movement import drive, gyro_set_origin, gyro_drive, gyro_turn

display_as = 2
color = Color.GREEN


def run():
    gyro_set_origin()

    gyro_drive(0, 60, sec(0.5))

    gyro_turn(90, 60, THEN(deg(90), sec(0.5)))
    gyro_drive(90, 60, sec(0.5))

    gyro_turn(180, 60, THEN(deg(165), sec(0.5)))
    gyro_drive(180, 60, sec(0.5))

    gyro_turn(270, 60, THEN(deg(-180), sec(0.5)))
    gyro_drive(270, 60, sec(0.5))

    gyro_turn(0, 60, THEN(deg(0), sec(0.5)))
    # -------------------
    # drive(gyro_drive_pid(0, speed(60)), sec(0.5))

    # drive(gyro_turn_pid(90, speed(60)), THEN(deg(90), sec(0.5)))
    # drive(gyro_drive_pid(90, speed(60)), sec(0.5))

    # drive(gyro_turn_pid(180, speed(60)), THEN(deg(165), sec(0.5)))
    # drive(gyro_drive_pid(180, speed(60)), sec(0.5))

    # drive(gyro_turn_pid(270, speed(60)), THEN(deg(-180), sec(0.5)))
    # drive(gyro_drive_pid(270, speed(60)), sec(0.5))

    # drive(gyro_turn_pid(0, speed(60)), THEN(deg(0), sec(0.5)))
    # -------------------

    # drive(speed(60), sec(0.5))

    # drive(speed(60, -60), THEN(deg(90), sec(0.5)))
    # drive(speed(60), sec(0.5))

    # drive(speed(60, -60), THEN(deg(165), sec(0.5)))
    # drive(speed(60), sec(0.5))

    # drive(speed(60, -60), THEN(deg(-180), sec(0.5)))
    # drive(speed(60), sec(0.5))

    # drive(speed(60, -60), THEN(deg(0), sec(0.5)))

    # drive(gyro_drive_pid(90, speed(60)), sec(1))
    # drive(gyro_drive_pid(90, speed(100)), sec(3))
    # gyro_drive(80, 0, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(180, p_correction=0.5, i_correction=0, d_correction=0)
    # gyro_drive(80, 180, sec(3), accelerate_for=1, decelerate_for=1)
    # gyro_turn(0, p_correction=0.5, i_correction=0, d_correction=0)

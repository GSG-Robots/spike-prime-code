import math
import time
# from sre_constants import POSSESSIVE_REPEAT_ONE

import color as col
import device
import hub

from ..gsgr.conditions import cm
from ..gsgr.config import cfg
from ..gsgr.enums import Sensor
from ..gsgr.movement import Pivot, gyro_drive, gyro_set_origin, gyro_turn

display_as = 9
color = col.PURPLE
left_sensor = Sensor.LIGHT
right_sensor = Sensor.LIGHT


def outside(measurement):
    return measurement[0] == 5 or (
        850 < measurement[2] < 950 and 650 < measurement[3] < 750 and 625 < measurement[4] < 750
    )


class Side:
    LEFT = 0
    RIGHT = 1


DISTANCE_LIGHT_SENSORS = 110
RADIUS_BASE = 483


def sonar_calc(driven_distance, gyro):
    connection_intersections = math.sqrt(
        DISTANCE_LIGHT_SENSORS**2
        + driven_distance**2
        - 2 * DISTANCE_LIGHT_SENSORS * driven_distance * math.cos(math.radians(90))
    )
    # Strecke1
    # print("connection_intersections", connection_intersections)

    angle1 = math.acos(
        (DISTANCE_LIGHT_SENSORS**2 + connection_intersections**2 - driven_distance**2)
        / (2 * DISTANCE_LIGHT_SENSORS * connection_intersections)
    )
    # Winkel4

    # print("angle1", math.degrees(angle1))

    angle2 = math.acos(
        (driven_distance**2 + connection_intersections**2 - DISTANCE_LIGHT_SENSORS**2)
        / (2 * driven_distance * connection_intersections)
    )
    # Winkel1

    angle2 = math.degrees(angle2)

    # print("angle2", angle2)

    angle3 = 90 - angle2
    # Winkel 2

    # print("angle3", angle3)

    angle4 = 180 - angle3 - gyro
    # Winkel5

    # print("angle4", angle4)

    angle5 = math.asin(connection_intersections / (2 * RADIUS_BASE))
    # Winkel3

    angle5 = math.degrees(angle5)

    # print("angle5", angle5)

    final_angle = angle4 + angle5

    return final_angle


def calc_way(start_angle, end_angle, distance):
    distance_to_drive = math.sqrt(
        RADIUS_BASE**2 + distance**2 - 2 * RADIUS_BASE * distance * math.cos(math.radians(end_angle - start_angle))
    )

    angle_to_drive = math.acos(
        (RADIUS_BASE**2 + distance_to_drive**2 - distance**2) / (2 * RADIUS_BASE * distance_to_drive)
    )

    return distance_to_drive, math.degrees(angle_to_drive)


# final_angle = sonar_calc(2, 90)
# print(final_angle)

# distance_to_drive, angle_to_drive = calc_way(final_angle, 15, 12)

# print(distance_to_drive, angle_to_drive)


def sonar(target_angle: int, distance: int):
    ergebnis = 0

    def end():
        nonlocal ergebnis
        for x in cm(2):
            yield x // 2
            if x >= 100:
                break

        first_side = None

        while True:
            left_measure = device.data(cfg.LEFT_SENSOR)
            right_measure = device.data(cfg.RIGHT_SENSOR)
            left = outside(left_measure)
            right = outside(right_measure)

            if left:
                first_side = Side.LEFT
                break

            if right:
                first_side = Side.RIGHT
                break

            yield 50

        first_left_abs = device.data(cfg.LEFT_MOTOR)[1]
        first_right_abs = device.data(cfg.RIGHT_MOTOR)[1]

        hub.light.color(hub.light.CONNECT, col.RED)

        second_side = None

        while True:
            left_measure = device.data(cfg.LEFT_SENSOR)
            right_measure = device.data(cfg.RIGHT_SENSOR)
            left = outside(left_measure)
            right = outside(right_measure)

            if left and first_side == Side.RIGHT:
                second_side = Side.LEFT
                break

            if right and first_side == Side.LEFT:
                second_side = Side.RIGHT
                break

            yield 50

        # Rad messen
        second_left_abs = device.data(cfg.LEFT_MOTOR)[1]
        second_right_abs = device.data(cfg.RIGHT_MOTOR)[1]
        hub.light.color(hub.light.CONNECT, col.GREEN)

        print(1234, first_right_abs, first_left_abs, second_left_abs, second_right_abs)

        delta_mit_vorzeichen = (
            (abs(second_right_abs - first_right_abs) + abs(second_left_abs - first_left_abs))
            / 72
            * cfg.TIRE_CIRCUMFRENCE
        )
        if first_side == Side.LEFT:
            delta_mit_vorzeichen *= -1
        print(
            delta_mit_vorzeichen,
            hub.motion_sensor.tilt_angles()[0] / 10,
            abs(hub.motion_sensor.tilt_angles()[0] / 10) + 90,
            sonar_calc(delta_mit_vorzeichen, abs(hub.motion_sensor.tilt_angles()[0] / 10) + 90),
        )
        ergebnis = sonar_calc(delta_mit_vorzeichen, abs(hub.motion_sensor.tilt_angles()[0] / 10) + 90) # ?? abs?

        for x in cm(5):
            yield 50 + x // 2

    print("HAALLLOOOO")

    # Grad messen
    gyro_drive(hub.motion_sensor.tilt_angles()[0] // 10, 700, end(), accelerate=10, decelerate=50, brake=True)
    distance_to_drive, angle_to_drive = calc_way(ergebnis, target_angle, distance)

    print(234, distance_to_drive, angle_to_drive)

    # target_angle_gyro = -(180 - angle_to_drive + ergebnis - 90)
    # menschzeil = (
    #     ergebnis + math.degrees(math.asin((distance_to_drive * math.sin(math.radians(angle_to_drive))) / distance)) * (1 if ergebnis < target_angle else -1)
    # )
    menschzeil = (180 - (90 - ergebnis) - angle_to_drive)
    target_angle_gyro = menschzeil - 90
    print("asdasd", menschzeil, target_angle_gyro)
    time.sleep(0.2)
    gyro_turn(target_angle_gyro, pivot=Pivot.LEFT_WHEEL)
    gyro_drive(target_angle_gyro, 700, cm(distance_to_drive / 10), accelerate=10, decelerate=30)


def run():
    gyro_set_origin()
    while hub.button.pressed(hub.button.POWER):
        ...
    while not hub.button.pressed(hub.button.POWER):
        ...
    while hub.button.pressed(hub.button.POWER):
        ...
    sonar(90 - 22.5, 700)
    gyro_turn(0, pivot=Pivot.LEFT_WHEEL)

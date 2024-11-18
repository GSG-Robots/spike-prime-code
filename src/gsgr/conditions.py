import math
import time
from .configuration import config
from .configuration import hardware as hw


def static(value: bool):
    while True:
        yield value


def cm(distance: int):
    start_degrees = hw.left_motor.get_degrees_counted()
    while True:
        yield (
            (
                abs(hw.right_motor.get_degrees_counted() - start_degrees)
                + abs(hw.left_motor.get_degrees_counted() - start_degrees)
            )
            / 360
            * math.pi
            * hw.tire_radius
        ) >= distance


def sec(duration: int):
    start_time = time.ticks_ms()
    while True:
        yield time.ticks_ms() > (duration * 1000 + start_time)


def deg(angle: int):
    print("bstarted at", config.degree_o_meter.oeioei)
    while True:
        yield (
            angle - config.gyro_tolerance / 2
            <= config.degree_o_meter.oeioei
            <= angle + config.gyro_tolerance / 2
        )


def line():
    return (
        hw.front_light_sensor.get_reflected_light() < config.light_black_value + 5
        or hw.back_light_sensor.get_reflected_light() < config.light_black_value + 5
    )

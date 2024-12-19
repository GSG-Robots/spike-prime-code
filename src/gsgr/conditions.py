import math
import time
from .configuration import config
from .configuration import hardware as hw


def static(value: bool):
    while True:
        yield value

def cm(distance: int):
    start_degrees = hw.left_motor.get_degrees_counted(), hw.right_motor.get_degrees_counted()
    while True:
        yield math.floor((
            (
                abs(hw.right_motor.get_degrees_counted() - start_degrees[1])
                + abs(hw.left_motor.get_degrees_counted() - start_degrees[0])
            )
            / 360
            * math.pi
            * hw.tire_radius
        ) / distance * 100)

def sec(duration: int):
    start_time = time.ticks_ms()
    while True:
        yield math.floor((time.ticks_ms() - start_time) / (duration * 1000) * 100)

def deg(angle: int):
    while True:
        yield 100 if (
            angle - config.gyro_tolerance / 2
            <= config.degree_o_meter.oeioei
            <= angle + config.gyro_tolerance / 2
        ) else 0

def THEN(first, second):
    while (a := next(first)) < 100:
        yield a // 2
    
    while (b := next(second)) < 100:
        yield 50 + b // 2
    
    yield 100

def OR(first, second):
    while True:
        yield next(first) or next(second)

def AND(first, second):
    while True:
        yield next(first) and next(second)

# def NOT(cond):
#     while True:
#         yield next(cond) < 100

def line():
    return (
        hw.front_light_sensor.get_reflected_light() < config.light_black_value + 5
        or hw.back_light_sensor.get_reflected_light() < config.light_black_value + 5
    )

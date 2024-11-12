# from collections import namedtuple
import math
import time

# from ._condition_base import ConditionBase
from .configuration import config
from .configuration import hardware as hw

# from .utils import Timer


#### class Infinite(ConditionBase): ...


#### class Cm(ConditionBase):
#     def __init__(self, value: int) -> None:
#         self.value = value

#     def setup(self):
#         hw.right_motor.set_degrees_counted(0)
#         hw.left_motor.set_degrees_counted(0)

#     def check(self):
#         return (
#             (
#                 abs(hw.right_motor.get_degrees_counted())
#                 + abs(hw.left_motor.get_degrees_counted())
#             )
#             / 360
#             * math.pi
#             * hw.tire_radius
#         ) >= self.value


#### class Sec(ConditionBase):
#     def __init__(self, value: int) -> None:
#         self.value = value
#         self.timer = Timer()

#     def setup(self):
#         self.timer.reset()

#     def check(self):
#         return self.timer.elapsed >= self.value


## class Line(ConditionBase):
##     def check(self, run):
##         return (
##             run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
##             or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
##         )


#### class Deg(ConditionBase):
#     def __init__(self, value: int) -> None:
#         self.value = value

#     def check(self):
#         return (
#             self.value - config.gyro_tolerance
#             <= hw.brick.motion_sensor.get_yaw_angle()
#             <= self.value + config.gyro_tolerance
#         )


def static(value: bool):
    return (0, value)


def cm(distance: int):
    return (
        1,
        distance,
    )


def sec(duration: int):
    return check(
        2,
        duration * 1000,
    )


def deg(angle: int):
    return (3, angle)


def check(type: int, value: int | tuple):
    if type == 0:
        while True:
            yield value

    elif type == 1:
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
            ) >= value

    elif type == 2:
        start_time = time.ticks_ms()
        while True:
            yield time.ticks_ms() > (value + start_time)

    elif type == 3:
        while True:
            yield (
                value - config.gyro_tolerance
                <= (config.degree_o_meter.turned)
                <= value + config.gyro_tolerance
            )

    else:
        while True:
            yield False

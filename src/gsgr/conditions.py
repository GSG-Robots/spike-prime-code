"""Basic conditions
"""

import math
import time
from .types import Condition
from .configuration import config
from .configuration import hardware as hw


def static(value: bool | int) -> Condition:
    """Static condition. Either always fulfilled or always unfulfilled.

    :param value: The static value to stay at. :py:obj:`True` means 100%, :py:obj:`False` means 0%.
    """
    while True:
        yield (100 if value else 0) if isinstance(value, bool) else value


def cm(distance: int) -> Condition:
    """Drive/Turn until wheels turned for given distance (cm)."""
    start_degrees = (
        hw.left_motor.get_degrees_counted(),
        hw.right_motor.get_degrees_counted(),
    )
    while True:
        yield math.floor(
            (
                (
                    abs(hw.right_motor.get_degrees_counted() - start_degrees[1])
                    + abs(hw.left_motor.get_degrees_counted() - start_degrees[0])
                )
                / 360
                * math.pi
                * hw.tire_radius
            )
            / distance
            * 100
        )


def sec(duration: int) -> Condition:
    """Drive/Turn for given duration (sec)."""
    start_time = time.ticks_ms()
    while True:
        yield math.floor((time.ticks_ms() - start_time) / (duration * 1000) * 100)


def deg(angle: int) -> Condition:
    """Drive/Turn until certain angle is reached."""
    while True:
        yield (
            100
            if (
                angle - config.gyro_tolerance / 2
                <= config.degree_o_meter.oeioei
                <= angle + config.gyro_tolerance / 2
            )
            else 0
        )


def THEN(first: Condition, second: Condition) -> Condition:
    """Helper to chain conditions.

    The two conditions are executed after each other. :py:obj:`THEN(cm(3), cm(5))` will have the same result as :py:obj:`cm(8)`
    """
    while (a := next(first)) <= 100:
        yield a // 2

    while (b := next(second)) <= 100:
        yield 50 + b // 2

    yield 100


def OR(first: Condition, second: Condition) -> Condition:
    """Helper to chain conditions.

    The two conditions are executed simultaneously, until one is fulfilled. :py:obj:`OR(cm(3), cm(5))` will have the same result as :py:obj:`cm(3)`
    """
    while True:
        yield max(next(first), next(second))


def AND(first: Condition, second: Condition) -> Condition:
    """Helper to chain conditions.

    The two conditions are executed simultaneously, until both are fulfilled. :py:obj:`AND(cm(3), cm(5))` will have the same result as :py:obj:`cm(5)`
    """
    while True:
        yield min(next(first), next(second))


def NOT(cond: Condition) -> Condition:
    """Helper to invert conditions."""
    while True:
        yield 100 - next(cond)


# def line():
#     return (
#         hw.front_light_sensor.get_reflected_light() < config.light_black_value + 5
#         or hw.back_light_sensor.get_reflected_light() < config.light_black_value + 5
#     )

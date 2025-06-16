"""Basic conditions"""

import math
import time

import hub
from gsgr.config import cfg

from .types import Condition


def static(value: bool | int, /) -> Condition:
    """Statische Bedingung. Dauerhaft entweder erfüllt oder nicht erfüllt.

    :param value: :py:obj:`True` bedeutet, dass die Bedingung dauerhaft erfüllt ist, :py:obj:`False` das Gegenteil.
    """
    yield 0
    while True:
        yield (100 if value else 0) if isinstance(value, bool) else value


def cm(distance: int, /) -> Condition:
    """... bis sich die Räder um eine Bestimmte Strecke bewegt haben.

    :param distance: Die Strecke, die zurückgelegt werden soll, in cm.
    """
    yield 0

    cfg.LEFT_MOTOR.mode([(2, 0)])
    cfg.RIGHT_MOTOR.mode([(2, 0)])

    start_degrees = (
        cfg.LEFT_MOTOR.get()[0],
        cfg.RIGHT_MOTOR.get()[0],
    )

    while True:
        yield math.floor(
            (
                (
                    abs(cfg.RIGHT_MOTOR.get()[0] - start_degrees[1])
                    + abs(cfg.LEFT_MOTOR.get()[0] - start_degrees[0])
                )
                / 720
                * cfg.TIRE_CIRCUMFRENCE
            )
            / distance
            * 100
        )


def sec(duration: int | float, /) -> Condition:
    """... bis eine bestimmte Zeit vergangen ist.

    :param duration: Die Dauer, die gewartet werden soll, in Sekunden.
    """
    yield 0

    start_time = time.ticks_ms()

    while True:
        yield math.floor((time.ticks_ms() - start_time) / (duration * 1000) * 100)


def impact(
    during: Condition, /, threshold: int | float = 500, min: int = 50
) -> Condition:
    yield 0

    sign = 0

    while True:
        parent = next(during)
        if parent >= min:
            break
        sign += math.copysign(1, hub.motion.accelerometer(filtered=False)[0])
        yield parent

    threshold = math.copysign(threshold, sign)

    while True:
        v = hub.motion.accelerometer(filtered=False)[0]
        if (v > threshold) if threshold > 0 else (v < threshold):
            break
        yield next(during)

    start_time = time.ticks_ms()

    while True:
        yield 90 + math.floor((time.ticks_ms() - start_time) / 50)


def pickup(
    during: Condition, /, threshold: int | float = 500, min: int = 50
) -> Condition:
    yield 0

    gs_avg = 981
    gs_cnt = 1

    while True:
        parent = next(during)
        if parent >= min:
            break
        gs_cnt += 1
        gs_avg = (
            gs_avg * (gs_cnt - 1) + hub.motion.accelerometer(filtered=False)[2]
        ) / gs_cnt
        yield parent

    threshold += gs_avg

    while True:
        v = hub.motion.accelerometer(filtered=False)[2]
        print(v, threshold)
        if v > threshold:
            break
        yield next(during)

    while True:
        yield 100


def deg(angle: int, /) -> Condition:
    """... bis der Roboter in eine bestimmte Richtung gedreht hat.

    :param angle: Der Winkel, in den der Roboter relativ zum Origin gedreht sein soll.
    """

    yield 0

    while True:
        yield (
            100
            if (
                angle - cfg.GYRO_TOLERANCE
                <= hub.motion.yaw_pitch_roll()[0]
                <= angle + cfg.GYRO_TOLERANCE
            )
            else 0
        )


def THEN(first: Condition, second: Condition, /) -> Condition:
    """... bis eine Bedingung erfüllt ist, und dann noch eine andere.

    Dabei werden die beiden Bedingungen nacheinander ausgeführt. :py:obj:`THEN(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(8)`

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """
    yield 0
    while (a := next(first)) < 100:
        yield a // 2

    while (b := next(second)) < 100:
        yield 50 + b // 2

    yield 100


def OR(first: Condition, second: Condition, /) -> Condition:
    """... bis eine von zwei Bedingungen erfüllt ist.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis mindestens eine erfüllt ist. :py:obj:`OR(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(3)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """
    yield 0

    while True:
        yield max(next(first), next(second))


def AND(first: Condition, second: Condition, /) -> Condition:
    """... bis beide von zwei Bedingungen erfüllt sind.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis beide erfüllt sind. :py:obj:`AND(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(5)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """
    yield 0

    while True:
        yield min(next(first), next(second))


def NOT(cond: Condition, /) -> Condition:
    """... bis eine Bedingung nicht erfüllt ist.

    :param cond: Die Bedingung, die nicht erfüllt sein soll.
    """
    yield 0

    while True:
        yield 100 - next(cond)


# TODO
# def line():
#     """... bis der Roboter eine Linie erkennt."""
#     return (
#         100
#         if (
#             hw.front_light_sensor.get_reflected_light()
#             < OLD_CONF_REPLACE.light_black_value + 5
#             or hw.back_light_sensor.get_reflected_light()
#             < OLD_CONF_REPLACE.light_black_value + 5
#         )
#         else 0
#     )

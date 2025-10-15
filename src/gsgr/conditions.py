"""Basic conditions"""

import math
import time

import hub
import motor

from .config import cfg
from .enums import SWSensor
from .types import Condition


def static(value: bool | int) -> Condition:
    """Statische Bedingung. Dauerhaft entweder erfüllt oder nicht erfüllt.

    :param value: :py:obj:`True` bedeutet, dass die Bedingung dauerhaft erfüllt ist, :py:obj:`False` das Gegenteil.
    """
    yield 0
    while True:
        yield (100 if value else 0) if isinstance(value, bool) else value


def cm(distance: int | float) -> Condition:
    """... bis sich die Räder um eine Bestimmte Strecke bewegt haben.

    :param distance: Die Strecke, die zurückgelegt werden soll, in cm.
    """
    yield 0

    start_degrees = (
        motor.relative_position(cfg.LEFT_MOTOR),
        motor.relative_position(cfg.RIGHT_MOTOR),
    )

    while True:
        yield math.floor(
            (
                (
                    abs(motor.relative_position(cfg.RIGHT_MOTOR) - start_degrees[1])
                    + abs(motor.relative_position(cfg.LEFT_MOTOR) - start_degrees[0])
                )
                / 720
                * cfg.TIRE_CIRCUMFRENCE
            )
            / distance
            * 100
        )


def wheels_blocked(chunk_size=100, threshold=10):
    la, lb = motor.relative_position(cfg.RIGHT_MOTOR), motor.relative_position(cfg.LEFT_MOTOR)
    since = time.ticks_ms() + 1000

    while True:
        if since + chunk_size < time.ticks_ms():
            a = motor.relative_position(cfg.RIGHT_MOTOR)
            b = motor.relative_position(cfg.LEFT_MOTOR)

            since = time.ticks_ms()
            difference = abs(la - a) + abs(lb - b)
            if difference < threshold:
                yield 100

            la, lb = a, b

        yield 0


def sec(duration: int | float) -> Condition:
    """... bis eine bestimmte Zeit vergangen ist.

    :param duration: Die Dauer, die gewartet werden soll, in Sekunden.
    """
    yield 0

    start_time = time.ticks_ms()

    while True:
        yield math.floor((time.ticks_ms() - start_time) / (duration * 1000) * 100)


def impact(during: Condition, threshold: int | float = 500, min: int = 50) -> Condition:
    yield 0

    sign = 0

    while True:
        parent = next(during)
        if parent >= min:
            break
        sign += math.copysign(1, hub.motion_sensor.acceleration(True)[0])
        yield parent

    threshold = math.copysign(threshold, sign)

    while True:
        v = hub.motion_sensor.acceleration(True)[0]
        if (v > threshold) if threshold > 0 else (v < threshold):
            break
        yield next(during)

    start_time = time.ticks_ms()

    while True:
        yield 90 + math.floor((time.ticks_ms() - start_time) / 50)


def pickup(during: Condition, threshold: int | float = 500, min: int = 50) -> Condition:
    yield 0

    gs_avg = 981
    gs_cnt = 1

    while True:
        parent = next(during)
        if parent >= min:
            break
        gs_cnt += 1
        gs_avg = (gs_avg * (gs_cnt - 1) + hub.motion_sensor.acceleration(True)[2]) / gs_cnt
        yield parent

    threshold += gs_avg

    while True:
        v = hub.motion_sensor.acceleration(True)[2]
        if v > threshold:
            break
        yield next(during)

    while True:
        yield 100


def deg(angle: int) -> Condition:
    """... bis der Roboter in eine bestimmte Richtung gedreht hat.

    :param angle: Der Winkel, in den der Roboter relativ zum Origin gedreht sein soll.
    """

    yield 0

    while True:
        yield (
            100 if (angle - cfg.GYRO_TOLERANCE <= hub.motion.yaw_pitch_roll()[0] <= angle + cfg.GYRO_TOLERANCE) else 0
        )


def light_left(threshold: float, below: bool = False):
    yield 0

    assert cfg.LEFT_SW_SENSOR in (
        SWSensor.INTEGRATED_LIGHT,
        SWSensor.EXTERNAL_LIGHT,
    ), "light_left: left sensor must be a light sensor"

    cfg.LEFT_SENSOR.mode(4)
    time.sleep(0.1)

    while below:
        yield 100 if cfg.LEFT_SENSOR.get(0)[0] / 10.24 < threshold else 0

    while True:
        yield 100 if cfg.LEFT_SENSOR.get(0)[0] / 10.24 > threshold else 0


def light_right(threshold: float, below: bool = False):
    yield 0

    assert cfg.RIGHT_SW_SENSOR in (
        SWSensor.INTEGRATED_LIGHT,
        SWSensor.EXTERNAL_LIGHT,
    ), "light_right: right sensor must be a light sensor"

    cfg.RIGHT_SENSOR.mode(4)
    time.sleep(0.1)

    while below:
        yield 100 if cfg.RIGHT_SENSOR.get(0)[0] / 10.24 < threshold else 0

    while True:
        yield 100 if cfg.RIGHT_SENSOR.get(0)[0] / 10.24 > threshold else 0


def THEN(first: Condition, second: Condition) -> Condition:
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


def OR(first: Condition, second: Condition) -> Condition:
    """... bis eine von zwei Bedingungen erfüllt ist.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis mindestens eine erfüllt ist. :py:obj:`OR(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(3)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """
    yield 0

    while True:
        yield max(next(first), next(second))


def AND(first: Condition, second: Condition) -> Condition:
    """... bis beide von zwei Bedingungen erfüllt sind.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis beide erfüllt sind. :py:obj:`AND(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(5)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """
    yield 0

    while True:
        yield min(next(first), next(second))


def NOT(cond: Condition) -> Condition:
    """... bis eine Bedingung nicht erfüllt ist.

    :param cond: Die Bedingung, die nicht erfüllt sein soll.
    """
    yield 0

    while True:
        yield 100 - next(cond)

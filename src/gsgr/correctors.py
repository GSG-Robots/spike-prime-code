"""Basic correctors
"""

import math

from .configuration import config
from .math import clamp, sigmoid
from .types import Corrector


def gyro_drive_pid(
    parent: Corrector,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
) -> Corrector:
    """Gyro Drive PID

    :param parent: Übergeordneter Corrector [TODO: Read more]
    :param degree_target: Zielfahrrichtung, zu der korrigiert werden soll
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: Toleranz für Zielgradzahl. Nutzt globale Konfiguration, falls nicht angegeben.
    """
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.gyro_drive_pid.p if p_correction is None else p_correction
    i_correction = config.gyro_drive_pid.i if i_correction is None else i_correction
    d_correction = config.gyro_drive_pid.d if d_correction is None else d_correction
    gyro_tolerance = config.gyro_tolerance if gyro_tolerance is None else gyro_tolerance

    yield next(parent)

    cur = config.degree_o_meter.oeioei
    last_error = error_value = min(
        (target - cur, target - cur - 360, target - cur + 360), key=abs
    )

    while True:
        left, right = next(parent)
        cur = config.degree_o_meter.oeioei
        error_value = min(
            (target - cur, target - cur - 360, target - cur + 360), key=abs
        )
        differential = error_value - last_error
        error_sum += error_value
        # math.copysign(1, error_value) != math.copysign(1, error_sum) or
        if abs(error_value) < gyro_tolerance:
            error_sum = 0
            differential = 0
            # error_value *= 2
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        yield (left + corrector, right - corrector)
        last_error = error_value


def speed(left, right=None) -> Corrector:
    """Statische Geschwindigkeit. Steht ganz oben in der Corrector-Kette.

    :param left: Geschwindigkeit für den linken Motor, bzw. beiden
    :param right: Geschwindigkeit für den rechten Motor. Entspricht :py:obj:`left`, falls nicht angegeben
    """
    right = right if right is not None else left
    while True:
        yield (left, right)


def gyro_turn_pid(
    parent: Corrector,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
) -> Corrector:
    """Gyro Turn PID

    :param parent: Übergeordneter Corrector [TODO: Read more]
    :param degree_target: Zieldrehung, zu der korrigiert werden soll
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: Toleranz für Zielgradzahl. Nutzt globale Konfiguration, falls nicht angegeben.
    """
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.gyro_turn_pid.p if p_correction is None else p_correction
    i_correction = config.gyro_turn_pid.i if i_correction is None else i_correction
    d_correction = config.gyro_turn_pid.d if d_correction is None else d_correction
    gyro_tolerance = config.gyro_tolerance if gyro_tolerance is None else gyro_tolerance

    while True:
        left, right = next(parent)
        tar, cur = target, config.degree_o_meter.oeioei
        error_value = min((tar - cur, tar - cur - 360, tar - cur + 360), key=abs)
        differential = error_value - last_error
        error_sum += error_value
        if abs(error_value) < gyro_tolerance:
            error_sum = 0
            differential = 0
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        last_error = error_value
        yield (corrector * (left / 100), -corrector * (right / 100))


def accelerate_linar(parent: Corrector, for_: int) -> Corrector:
    """Lineare Beschleunigung

    :param parent: Übergeordneter Corrector [TODO: Read more]
    :param for_: Dauer der Beschleunigung als Condition
    """
    while True:
        left, right = next(parent)
        speed_mutiplier = clamp(next(for_) / 100, 0.1, 1)
        yield (left * speed_mutiplier, right * speed_mutiplier)


def decelerate(parent: Corrector, from_: int, for_: int) -> Corrector:
    """Lineare Entschleunigung

    :param parent: Übergeordneter Corrector [TODO: Read more]
    :param start: Startzeitpunkt der Entschleunigung als Condition
    :param duration: Dauer der Entschleunigung als Condition
    """
    while True:
        left, right = next(parent)
        if next(from_) < 100:
            yield left, right
        else:
            speed_mutiplier = 1 - clamp(next(for_) / 100, 0.1, 1)
            yield (left * speed_mutiplier, right * speed_mutiplier)


def accelerate_sigmoid(
    parent: Corrector, for_: int, smooth: int = 6, stretch: bool = True
) -> Corrector:
    """Sigmoid Beschleunigung

    :param parent: Übergeordneter Corrector [TODO: Read more]
    :param for_: Dauer der Beschleunigung als Condition
    :param smooth: Glättungsfaktor für die Sigmoid-Funktion
    :param stretch: Ob die Sigmoid-Funktion gestreckt werden soll
    """
    cutoff = sigmoid(-smooth) if stretch else 0
    while True:
        left, right = next(parent)
        speed_mutiplier = clamp(
            round(
                (sigmoid((next(for_) / 100 * 2 * smooth) - smooth) - cutoff)
                / (1 - cutoff),
                2,
            ),
            0,
            1,
        )
        yield (
            clamp(left * speed_mutiplier, 10, 100),
            clamp(right * speed_mutiplier, 10, 100),
        )

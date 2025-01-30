"""Basic correctors
"""

from .types import Corrector
from .utils import Timer
from .configuration import config
from .math import clamp, sigmoid


def gyro_drive_pid(
    parent: Corrector,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
) -> Corrector:
    """Gyro Drive PID

    :param parent: Parent corrector [TODO: Read more]
    :param degree_target: Direction to drive in/correct towards to
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: tolerance for target degree. Defaults to general config.
    """
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.p_correction if p_correction is None else p_correction
    i_correction = config.i_correction if i_correction is None else i_correction
    d_correction = config.d_correction if d_correction is None else d_correction
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
        yield (left + corrector, right - corrector)


def speed(left, right=None) -> Corrector:
    """Static speed. Used at the top of a corrector chain.

    :param left: Speed of left motor.
    :param right: Speed of right motor. Defaults to :py:obj:`left`.
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

    :param parent: Parent corrector [TODO: Read more]
    :param degree_target: Direction to turn to
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: tolerance for target degree. Defaults to general config.
    """
    target = degree_target
    while target < -180:
        target += 360
    while target > 180:
        target -= 360
    last_error = 0
    error_sum = 0
    p_correction = config.p_correction if p_correction is None else p_correction
    i_correction = config.i_correction if i_correction is None else i_correction
    d_correction = config.d_correction if d_correction is None else d_correction
    gyro_tolerance = config.gyro_tolerance if gyro_tolerance is None else gyro_tolerance

    while True:
        left, right = next(parent)
        tar, cur = target, config.degree_o_meter.oeioei
        error_value = min((tar - cur, tar - cur - 360, tar - cur + 360), key=abs)
        differential = error_value - last_error
        error_sum += error_value
        if error_value < gyro_tolerance:
            error_sum = 0
            differential = 0
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        last_error = error_value
        yield (corrector * (left / 100), -corrector * (right / 100))


def pause(parent: Corrector, start: int, duration: int) -> Corrector:
    """Auxiliary corrector to pause in a specific time range.

    :param parent: Parent corrector [TODO: Read more]
    :param start: Amount of seconds to stop after.
    :param duration: Amount of seconds to stop for.
    """
    timer = Timer()
    while True:
        if start < timer.elapsed < (start + duration):
            yield (0, 0)
        yield next(parent)


def accelerate_linar(
    parent: Corrector, for_: int, start_at: int | None = None
) -> Corrector:
    """Auxiliary corrector to accelerate in a specific time range.

    :param parent: Parent corrector [TODO: Read more]
    :param for_: Amount of seconds to accelerate for.
    :param start_at: Amount of seconds to delay accelerating.
    """
    while True:
        left, right = next(parent)
        if start_at is not None and next(start_at) < 100:
            yield left, right
        else:
            speed_mutiplier = clamp(next(for_) / 100, 0.5, 1)
            yield (left * speed_mutiplier, right * speed_mutiplier)


def decelerate(parent: Corrector, from_: int, for_: int) -> Corrector:
    """Auxiliary corrector to deccelerate in a specific time range.

    :param parent: Parent corrector [TODO: Read more]
    :param start: Amount of seconds to deccelerate after.
    :param duration: Amount of seconds to deccelerate for.
    """
    while True:
        left, right = next(parent)
        if next(from_) < 100:
            yield left, right
        else:
            speed_mutiplier = 1 - clamp(next(for_) / 100, 0.5, 1)
            yield (left * speed_mutiplier, right * speed_mutiplier)


def sigmoid_accelerate_sec(
    parent: Corrector, duration: int, smooth: int = 6, stretch: bool = True
) -> Corrector:
    """Auxiliary corrector to accelerate in a specific time range, softened using the sigmoid function.

    TODO: WTH is smooth & stretch again?

    :param parent: Parent corrector [TODO: Read more]
    :param duration: Amount of seconds to accelerate for.
    """

    #:param smooth: Amount of seconds to delay accelerating.

    timer = Timer()
    cutoff = sigmoid(-smooth) if stretch else 0
    while True:
        left, right = next(parent)
        now = timer.elapsed
        speed_mutiplier = clamp(
            round(
                (sigmoid((clamp(now / duration, 0, 1) * 2 * smooth) - smooth) - cutoff)
                / (1 - cutoff),
                2,
            ),
            0,
            1,
        )
        yield (left * speed_mutiplier, right * speed_mutiplier)


def accelerate_sigmoid(
    parent: Corrector, for_: int, smooth: int = 6, stretch: bool = True
) -> Corrector:
    """Auxiliary corrector to accelerate in a specific time range.

    :param parent: Parent corrector [TODO: Read more]
    :param for_: Amount of seconds to accelerate for.
    :param start_at: Amount of seconds to delay accelerating.
    """
    cutoff = sigmoid(-smooth) if stretch else 0
    while True:
        left, right = next(parent)
        speed_mutiplier = clamp(
            round(
                (
                    sigmoid((next(for_) / 100 * 2 * smooth) - smooth)
                    - cutoff
                )
                / (1 - cutoff),
                2,
            ),
            0,
            1,
        )
        yield (clamp(left * speed_mutiplier, 25, 100), clamp(right * speed_mutiplier, 25, 100))

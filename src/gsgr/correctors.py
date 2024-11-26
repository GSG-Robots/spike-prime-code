import abc

from gsgr.utils import Timer

from .configuration import config
from .configuration import hardware as hw
from .math import clamp, sigmoid


class Corrector(abc.ABC):
    @abc.abstractmethod
    def apply(
        self, left: float | int, right: float | int
    ) -> tuple[float | int, float | int]: ...
    @abc.abstractmethod
    def setup(self) -> None: ...


def gyro_drive_pid(
    parent,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
):
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
        yield (left + corrector, right - corrector)


def speed(left, right=None):
    right = right if right is not None else left
    while True:
        yield (left, right)


def gyro_turn_pid(
    parent,
    degree_target: int,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
    gyro_tolerance: int | None = None,
):
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


def pause(parent, start: int, duration: int):
    timer = Timer()
    while True:
        if start < timer.elapsed < (start + duration):
            yield (0, 0)
        yield next(parent)


def accelerate_sec(parent, duration: int, start: int = 0):
    timer = Timer()
    while True:
        left, right = next(parent)
        speed_mutiplier = clamp(max(timer.elapsed - start, 0) / duration, 0, 1)
        yield (left * speed_mutiplier, right * speed_mutiplier)


def decelerate_sec(parent, duration: int, start: int = 0):
    timer = Timer()
    while True:
        left, right = next(parent)
        speed_mutiplier = 1 - clamp(max(timer.elapsed - start, 0) / duration, 0, 1)
        yield (left * speed_mutiplier, right * speed_mutiplier)


def sigmoid_accelerate_sec(
    parent, duration: int, smooth: int = 6, stretch: bool = True
):
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

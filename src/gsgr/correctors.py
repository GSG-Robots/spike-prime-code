import abc

from .configuration import config
from .configuration import hardware as hw
from .math import clamp, sigmoid
from .utils import Timer


class Corrector(abc.ABC):
    @abc.abstractmethod
    def apply(
        self, left: float | int, right: float | int
    ) -> tuple[float | int, float | int]: ...
    @abc.abstractmethod
    def setup(self) -> None: ...


class GyroDrivePID(Corrector):
    def __init__(
        self,
        degree_target: int,
        p_correction: float | None = None,
        i_correction: float | None = None,
        d_correction: float | None = None,
    ) -> None:
        self.target = degree_target - config.degree_offset
        self.last_error = 0
        self.error_sum = 0
        self.p_correction = (
            config.p_correction if p_correction is None else p_correction
        )
        self.i_correction = (
            config.i_correction if i_correction is None else i_correction
        )
        self.d_correction = (
            config.d_correction if d_correction is None else d_correction
        )

    def setup(self): ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        error_value = self.target - config.degree_o_meter.turned
        while error_value > 180:
            error_value -= 360
        while error_value <= -180:
            error_value += 360
        differential = error_value - self.last_error
        self.error_sum += error_value
        if error_value < config.error_threshold:
            self.error_sum = 0
            differential = 0
        corrector = (
            self.error_sum * self.i_correction
            + differential * self.d_correction
            + error_value * self.p_correction
        )
        self.last_error = error_value
        return (left + corrector, right - corrector)


def speed(left, right=None):
    right = right if right is not None else left
    while True:
        yield (left, right)


def gyro_turn_pid(
    degree_target: int,
    parent,
    p_correction: float | None = None,
    i_correction: float | None = None,
    d_correction: float | None = None,
):
    p_correction = config.p_correction if p_correction is None else p_correction
    i_correction = config.i_correction if i_correction is None else i_correction
    d_correction = config.d_correction if d_correction is None else d_correction
    target = degree_target - config.degree_offset
    print(target)

    last_error = 0
    error_sum = 0

    while True:
        left, right = next(parent)
        error_value = target - config.degree_o_meter.turned
        while error_value > 180:
            error_value -= 360
        while error_value <= -180:
            error_value += 360
        differential = error_value - last_error
        error_sum += error_value
        if error_value < config.error_threshold:
            error_sum = 0
            differential = 0
        corrector = (
            error_sum * i_correction
            + differential * d_correction
            + error_value * p_correction
        )
        last_error = error_value
        yield (left + corrector * (left / 100), right - corrector * (right / 100))


class GyroTurnPID(Corrector):
    def __init__(
        self,
        degree_target: int,
        p_correction: float | None = None,
        i_correction: float | None = None,
        d_correction: float | None = None,
    ) -> None:
        self.target = degree_target - config.degree_offset
        self.last_error = 0
        self.error_sum = 0
        self.p_correction = (
            config.p_correction if p_correction is None else p_correction
        )
        self.i_correction = (
            config.i_correction if i_correction is None else i_correction
        )
        self.d_correction = (
            config.d_correction if d_correction is None else d_correction
        )

    def setup(self) -> None: ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        error_value = self.target - config.degree_o_meter.turned
        while error_value > 180:
            error_value -= 360
        while error_value <= -180:
            error_value += 360
        differential = error_value - self.last_error
        self.error_sum += error_value
        if error_value < config.error_threshold:
            self.error_sum = 0
            differential = 0
        corrector = (
            self.error_sum * self.i_correction
            + differential * self.d_correction
            + error_value * self.p_correction
        )
        self.last_error = error_value
        return (corrector * (left / 100), -corrector * (right / 100))


class Pause(Corrector):
    def __init__(self, at: int, duration: int) -> None:
        self.start = at
        self.duration = duration
        self.timer = Timer()

    def setup(self): ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        if self.start < self.timer.elapsed < (self.start + self.duration):
            return (0, 0)
        return (left, right)


class AccelerateSec(Corrector):
    def __init__(self, duration: int, delay: int = 0) -> None:
        self.delay = delay
        self.duration = duration
        self.timer = Timer()

    def setup(self): ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        speed_mutiplier = clamp(
            max(self.timer.elapsed - self.delay, 0) / self.duration, 0, 1
        )
        return (left * speed_mutiplier, right * speed_mutiplier)


# class AccelerateCm(Corrector):
#     def __init__(self, duration: int, delay: int = 0) -> None:
#         self.delay = delay
#         self.duration = duration
#         self.timer = Timer()

#     def apply(
#         self, left: int | float, right: int | float
#     ) -> tuple[float | int, float | int]:
#         speed_mutiplier = clamp(
#             max(self.timer.elapsed - self.delay, 0) / self.duration, 0, 1
#         )
#         return (left * speed_mutiplier, right * speed_mutiplier)


class DecelerateSec(Corrector):
    def __init__(self, duration: int, delay: int = 0) -> None:
        self.delay = delay
        self.duration = duration
        self.timer = Timer()

    def setup(self): ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        speed_mutiplier = 1 - clamp(
            max(self.timer.elapsed - self.delay, 0) / self.duration, 0, 1
        )
        return (left * speed_mutiplier, right * speed_mutiplier)


# class DecelerateCm(Corrector):
#     def __init__(self, duration: int, delay: int = 0) -> None:
#         self.delay = delay
#         self.duration = duration
#         self.started_at = 0

#     def apply(
#         self, left: int | float, right: int | float
#     ) -> tuple[float | int, float | int]:
#         speed_mutiplier = 1 - clamp(
#             max(self.timer.elapsed - self.delay, 0) / self.duration, 0, 1
#         )
#         return (left * speed_mutiplier, right * speed_mutiplier)


class SigmoidAcceleration(Corrector):
    def __init__(self, duration: int, smooth: int = 6, stretch: bool = True) -> None:
        self.duration = duration
        self.timer = Timer()
        self.smooth = smooth
        self.cutoff = sigmoid(-smooth) if stretch else 0

    def setup(self): ...

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        now = self.timer.elapsed
        speed_mutiplier = clamp(
            round(
                (
                    sigmoid(
                        (clamp(now / self.duration, 0, 1) * 2 * self.smooth)
                        - self.smooth
                    )
                    - self.cutoff
                )
                / (1 - self.cutoff),
                2,
            ),
            0,
            1,
        )
        return (left * speed_mutiplier, right * speed_mutiplier)

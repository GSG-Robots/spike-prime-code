import time
from spike.control import Timer
from .configuration import config, hardware as hw


class Corrector:
    def apply(
        self, left: float | int, right: float | int
    ) -> tuple[float | int, float | int]: ...


class GyroDrivePIDCorrector(Corrector):
    def __init__(
        self,
        degree_target: int,
        p_correction: float | None = None,
        i_correction: float | None = None,
        d_correction: float | None = None,
    ) -> None:
        self.target = degree_target
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

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        error_value = self.target - hw.brick.motion_sensor.get_yaw_angle()
        while error_value > 180:
            error_value -= 360
        while error_value <= -180:
            error_value += 360
        differential = error_value - self.last_error
        self.error_sum += error_value
        corrector = (
            self.error_sum * self.i_correction
            + differential * self.d_correction
            + error_value * self.p_correction
        )
        self.last_error = error_value
        return (left + corrector, right - corrector)


class AccelerationSecCorrecor(Corrector):
    def __init__(self, duration: int) -> None:
        self.duration = duration
        self.started_at = time.ticks_ms()

    def apply(
        self, left: int | float, right: int | float
    ) -> tuple[float | int, float | int]:
        now = time.ticks_diff(time.ticks_ms(), self.started_at) / 1000
        print(time.ticks_ms())
        speed_mutiplier = min(1.0, now / self.duration)
        print(speed_mutiplier, now, self.duration, now / self.duration)
        return (left * speed_mutiplier, right * speed_mutiplier)

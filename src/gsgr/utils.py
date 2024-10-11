import time
from .configuration import hardware as hw


class Timer:
    def __init__(self) -> None:
        self.started_at = time.ticks_ms()

    def reset(self) -> None:
        self.started_at = time.ticks_ms()

    @property
    def elapsed(self) -> float:
        return time.ticks_diff(time.ticks_ms(), self.started_at) / 1000

    @property
    def elapsed_ms(self) -> float:
        return time.ticks_diff(time.ticks_ms(), self.started_at)


class DegreeOMeter:
    def __init__(self) -> None:
        self.started_at = hw.brick.motion_sensor.get_yaw_angle()

    def reset(self, offset=0) -> None:
        self.started_at = hw.brick.motion_sensor.get_yaw_angle() - offset

    @property
    def turned(self) -> float:
        return hw.brick.motion_sensor.get_yaw_angle() - self.started_at

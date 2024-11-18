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
        if self.started_at < -180:
            self.started_at += 360

    @property
    def oeioei(self) -> float:
        """-180 to 180"""
        res = hw.brick.motion_sensor.get_yaw_angle() - self.started_at
        if res < -180:
            res += 360
        if res > 180:
            res -= 360
        return res
    
    @property
    def zts(self) -> float:
        "0 to 360"
        return oeioei_to_zts(self.oeioei)


def zts_to_oeioei(zts):
    if zts < 0:
        return zts - 360
    return zts

def oeioei_to_zts(oeioei):
    if oeioei < 0:
        return oeioei + 360
    return oeioei
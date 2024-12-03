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
        self.started_at = 0

    def reset(self, offset=0) -> None:
        # self.started_at =  self._get_yaw_angle() - offset
        # if self.started_at < -180:
        #     self.started_at += 360
        # if self.started_at > 180:
        #     self.started_at -= 360
        self.started_at = 0
        hw.brick.motion_sensor.reset_yaw_angle()
        
    def _get_yaw_angle(self):
        deg = hw.brick.motion_sensor.get_yaw_angle()
        # deg += 146
        # if deg >= 292:
        #     deg -= 292
        # deg -= 146
        # print(deg, deg / 73 * 90)
        return deg# / 73 * 90

    @property
    def oeioei(self) -> float:
        """-180 to 180"""
        res = self._get_yaw_angle() - self.started_at
        if res < -180:
            res += 360
        if res > 180:
            res -= 360
        print(88, res)
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
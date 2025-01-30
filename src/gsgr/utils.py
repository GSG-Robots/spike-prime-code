import time

from .configuration import hardware as hw


class Timer:
    """Helper class to time things."""

    started_at: int
    """Timestamp of last reset
    """

    def __init__(self) -> None:
        self.started_at = time.ticks_ms()

    def reset(self) -> None:
        """Reset the timer."""
        self.started_at = time.ticks_ms()

    @property
    def elapsed(self) -> float:
        """Elapsed time in seconds."""
        return time.ticks_diff(time.ticks_ms(), self.started_at) / 1000

    @property
    def elapsed_ms(self) -> float:
        """Elapsed time in milliseconds."""
        return time.ticks_diff(time.ticks_ms(), self.started_at)


class DegreeOMeter:
    """Helper class to measure directions relatively to each other."""

    started_at: int
    """Zero-point offset to action gyro sensor values.
    """

    def __init__(self) -> None:
        self.started_at = 0

    def reset(self, offset: int = 0) -> None:
        """Set current direction as origin.

        :param offset: Unused.
        """
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
        return deg  # / 73 * 90

    @property
    def oeioei(self) -> float:
        """Current direction relative to selected origin in -180 to 180 range."""
        res = self._get_yaw_angle() - self.started_at
        if res < -180:
            res += 360
        if res > 180:
            res -= 360
        return res

    @property
    def zts(self) -> float:
        """Current direction relative to selected origin in 0 to 360 range."""
        return oeioei_to_zts(self.oeioei)


def zts_to_oeioei(zts: int | float) -> int | float:
    """Helper function to convert 0 to 360deg angle to -180 to 180deg angle."""
    if zts < 0:
        return zts - 360
    return zts


def oeioei_to_zts(oeioei: int | float) -> int | float:
    """Helper function to convert -180 to 180deg angle to 0 to 360deg angle."""
    if oeioei < 0:
        return oeioei + 360
    return oeioei

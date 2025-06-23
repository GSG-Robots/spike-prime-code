import time


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

import time


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

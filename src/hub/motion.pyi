from collections.abc import Callable
from typing import overload

TAPPED = 0
DOUBLETAPPED = 1
SHAKE = 2
FREEFALL = 3

def accelerometer(filtered: bool = False) -> tuple[int, int, int]: ...
def gyroscope(filtered: bool = False) -> tuple[int, int, int]: ...
@overload
def align_to_model(top: int, front: int) -> None: ...
@overload
def align_to_model(nsamples: int, callback: Callable[[int], None]) -> None: ...
@overload
def align_to_model(top: int, front: int, nsamples: int, callback: Callable[[int], None]) -> None: ...
@overload
def yaw_pitch_roll() -> tuple[int, int, int]: ...
@overload
def yaw_pitch_roll(yaw_preset: int) -> None: ...
@overload
def yaw_pitch_roll(yaw_correction: float) -> None: ...
@overload
def orientation() -> int: ...
@overload
def orientation(callback: Callable[[int], None]) -> int: ...
@overload
def gesture() -> int: ...
@overload
def gesture(callback: Callable[[int], None]) -> int: ...

__all__ = [
    "TAPPED",
    "DOUBLETAPPED",
    "SHAKE",
    "FREEFALL",
    "accelerometer",
    "gyroscope",
    "align_to_model",
    "yaw_pitch_roll",
    "orientation",
    "gesture",
]

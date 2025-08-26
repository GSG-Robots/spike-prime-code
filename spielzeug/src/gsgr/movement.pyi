"""Motorsteuerung und Bewegungsfunktionen."""

from collections.abc import Generator

from typing_extensions import Literal

from .config import PID
from .enums import Pivot
from .interpolators import linear

def check_battery(): ...
def hold_attachment(target_gear: int, await_completion: bool = True): ...
def free_attachment(target_gear: int, await_completion: bool = True): ...
def free_attachments(): ...
def run_attachment(
    attachment: int,
    speed: int,
    duration: int | float | None = None,
    stall: bool = False,
    untension: int | None = None,
    await_completion: bool = True,
) -> None: ...
def stop_attachment(
    untension: int | Literal[False] = False, await_completion: bool = False
): ...
def gyro_set_origin(): ...
def gyro_wall_align(backwards=False, wall_align_duration=None): ...
def gyro_turn(
    target_angle: int,
    step_speed: int | float = 70,
    pivot: Pivot | int = Pivot.CENTER,
    min_speed: int | None = None,
    max_speed: int | None = None,
    pid: PID | None = None,
    tolerance: int | None = None,
    timeout: int = 0,
    brake: bool = True,
): ...
def gyro_drive(
    target_angle: int,
    speed: int | float,
    ending_condition: Generator,
    pid: PID | None = None,
    accelerate: float = 0,
    decelerate: float = 0,
    interpolators=(linear, linear),
    brake: bool = True,
): ...

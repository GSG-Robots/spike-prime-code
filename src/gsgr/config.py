import math
from collections import namedtuple
from typing import Any, Callable, Self, TypeVar

import hub

PID = namedtuple("PID", ("p", "i", "d"))

PORTS = {
    "A": hub.port.A,
    "B": hub.port.B,
    "C": hub.port.C,
    "D": hub.port.D,
    "E": hub.port.E,
    "F": hub.port.F,
}

T = TypeVar("T")


# For Type-Hinting, comPYner will handle @compile specially
def compile(f: Callable[[str], T]) -> T:
    return f(__file__)


@compile
def _config_dict(in_file) -> dict[str, Any]:
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    import yaml  # pylint: disable=import-outside-toplevel

    file: Path = Path(in_file).absolute().parent / ".." / "config.yaml"

    with file.open("r", encoding="utf-8") as f:
        return yaml.load(f, yaml.Loader)


class configure:
    def __init__(self, **kwargs) -> None:
        self.changes: dict[str, Any] = kwargs
        self.old: dict[str, Any] = {}

    def gyro_drive(self, pid: PID) -> Self:
        self.changes["GYRO_DRIVE_PID"] = pid
        return self

    def gyro_turn(
        self, pid: PID | None = None, minmax_speed: tuple[int, int] | None = None
    ) -> Self:
        if pid is not None:
            self.changes["GYRO_TURN_PID"] = pid
        if minmax_speed is not None:
            self.changes["GYRO_TURN_MINMAX_SPEED"] = minmax_speed
        return self

    def debug_mode(self, enabled: bool) -> Self:
        self.changes["DEBUG_MODE"] = enabled
        return self

    def gyro_tolerance(self, tolernce: int) -> Self:
        self.changes["GYRO_TOLERANCE"] = tolernce
        return self

    def __enter__(self):
        for key, value in self.changes:
            self.old[key] = getattr(cfg, key)
            setattr(cfg, key, value)

    def __exit__(self):
        for key, value in self.old:
            setattr(cfg, key, value)


class Config:
    LEFT_MOTOR: hub.Motor
    RIGHT_MOTOR: hub.Motor
    DRIVING_MOTORS: hub.MotorPair
    GEAR_SHAFT: hub.Motor
    GEAR_SELECTOR: hub.Motor
    TIRE_CIRCUMFRENCE: float
    DEBUG_MODE: bool
    LOOP_THROTTLE: float
    GYRO_TOLERANCE: int
    GYRO_DRIVE_PID: PID
    GYRO_TURN_PID: PID
    GYRO_TURN_MINMAX_SPEED: tuple[int, int]

    def __init__(self):
        self.LEFT_MOTOR = PORTS[_config_dict["driving_motors"]["left"]].motor
        self.RIGHT_MOTOR = PORTS[_config_dict["driving_motors"]["right"]].motor
        self.DRIVING_MOTORS = self.LEFT_MOTOR.pair(self.RIGHT_MOTOR)
        if not self.DRIVING_MOTORS:
            raise ValueError("Motors cannot be paired")
        self.GEAR_SHAFT = PORTS[_config_dict["gearbox"]["drive_shaft"]].motor
        self.GEAR_SELECTOR = PORTS[_config_dict["gearbox"]["gear_selector"]].motor
        self.TIRE_CIRCUMFRENCE = _config_dict["tire_diameter"] * math.pi
        self.DEBUG_MODE = _config_dict["debug_mode"]
        self.LOOP_THROTTLE = _config_dict["loop_throttle"]
        self.GYRO_TOLERANCE = _config_dict["gyro_tolerance"]
        self.GYRO_DRIVE_PID = PID(
            _config_dict["correctors"]["gyro_drive"]["p"],
            _config_dict["correctors"]["gyro_drive"]["i"],
            _config_dict["correctors"]["gyro_drive"]["d"],
        )
        self.GYRO_TURN_PID = PID(
            _config_dict["correctors"]["gyro_turn"]["p"],
            _config_dict["correctors"]["gyro_turn"]["i"],
            _config_dict["correctors"]["gyro_turn"]["d"],
        )
        self.GYRO_TURN_MINMAX_SPEED = (
            _config_dict["correctors"]["gyro_turn"]["min_speed"],
            _config_dict["correctors"]["gyro_turn"]["max_speed"],
        )

        # Presets:
        #   Disables native acceleration, deceleration, correction and differential lock
        # self.LEFT_MOTOR.default(
        #     speed=70,
        #     max_power=100,
        #     acceleration=100,
        #     deceleration=100,
        #     stop=1,
        #     pid=(10, 0, 0),
        #     stall=False,
        #     callback=self.LEFT_MOTOR.default()["callback"],
        # )
        # self.RIGHT_MOTOR.default(
        #     speed=70,
        #     max_power=100,
        #     acceleration=100,
        #     deceleration=100,
        #     stop=1,
        #     pid=(10, 0, 0),
        #     stall=False,
        #     callback=self.RIGHT_MOTOR.default()["callback"],
        # )
        self.DRIVING_MOTORS.pid(0, 0, 0)
        self.GEAR_SHAFT.default(
            speed=100,
            max_power=100,
            acceleration=300,
            deceleration=300,
            stop=1,
            pid=(0, 0, 0),
            stall=True,
            callback=self.GEAR_SHAFT.default()["callback"],
        )
        self.GEAR_SELECTOR.default(
            speed=100,
            max_power=100,
            acceleration=300,
            deceleration=300,
            stop=2,
            pid=(0, 0, 0),
            stall=False,
            callback=self.GEAR_SELECTOR.default()["callback"],
        )


cfg = Config()


__all__ = ["cfg", "PID", "configure"]

import math
from collections import namedtuple
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


# For Type-Hinting, comPYner will handle @compile specially
def compile(f):
    return f(__file__)


@compile
def _config_dict(in_file):
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    import yaml  # pylint: disable=import-outside-toplevel

    file = Path(in_file).absolute().parent / ".." / "config.yaml"

    with file.open("r", encoding="utf-8") as file:
        return yaml.load(file, yaml.Loader)


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

cfg = Config()


__all__ = ["cfg", "PID"]

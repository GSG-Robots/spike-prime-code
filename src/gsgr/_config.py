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


@compile
def _config_dict(in_file):
    from pathlib import Path  # pylint: disable=import-outside-toplevel

    import yaml  # pylint: disable=import-outside-toplevel

    file = Path(in_file).absolute().parent / ".." / "config.yaml"

    with file.open("r", encoding="utf-8") as file:
        return yaml.load(file, yaml.Loader)


LEFT_MOTOR: hub.Motor = PORTS[_config_dict["driving_motors"]["left"]].motor
RIGHT_MOTOR: hub.Motor = PORTS[_config_dict["driving_motors"]["right"]].motor
DRIVING_MOTORS: hub.MotorPair = LEFT_MOTOR.pair(RIGHT_MOTOR)
if not DRIVING_MOTORS:
    raise ValueError("Motors cannot be paired")
GEAR_SHAFT: hub.Motor = PORTS[_config_dict["gearbox"]["drive_shaft"]].motor
GEAR_SELECTOR: hub.Motor = PORTS[_config_dict["gearbox"]["gear_selector"]].motor
TIRE_CIRCUMFRENCE: float = _config_dict["tire_diameter"] * math.pi
DEBUG_MODE: bool = _config_dict["debug_mode"]
LOOP_THROTTLE: float = _config_dict["loop_throttle"]
GYRO_DRIVE_PID = PID(
    _config_dict["correctors"]["gyro_drive"]["p"],
    _config_dict["correctors"]["gyro_drive"]["i"],
    _config_dict["correctors"]["gyro_drive"]["d"],
)
GYRO_TURN_PID = PID(
    _config_dict["correctors"]["gyro_turn"]["p"],
    _config_dict["correctors"]["gyro_turn"]["i"],
    _config_dict["correctors"]["gyro_turn"]["d"],
)
GYRO_TOLERANCE = _config_dict["gyro_tolerance"]
GYRO_DRIVE2_PID = PID(
    _config_dict["correctors"]["gyro_drive2"]["p"],
    _config_dict["correctors"]["gyro_drive2"]["i"],
    _config_dict["correctors"]["gyro_drive2"]["d"],
)
GYRO_SPEED_TURN_PID = PID(
    _config_dict["correctors"]["gyro_speed_turn"]["p"],
    _config_dict["correctors"]["gyro_speed_turn"]["i"],
    _config_dict["correctors"]["gyro_speed_turn"]["d"],
)
GYRO_SPEED_TURN_MINMAX_SPEED = (
    _config_dict["correctors"]["gyro_speed_turn"]["min_speed"],
    _config_dict["correctors"]["gyro_speed_turn"]["max_speed"],
)
I_LAST_SHAFT_SPEED = 0
I_SELECTOR_STATE = 0

@GEAR_SELECTOR.callback
def _cb(stat):
    global I_SELECTOR_STATE
    I_SELECTOR_STATE = stat
    print("newstat", stat)

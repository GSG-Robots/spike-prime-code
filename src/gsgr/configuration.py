import spike
from ._config_base import ConfigBase


class Config(ConfigBase):
    "The configuration for the robot"

    debug_mode: bool
    "Whether the debug mode should be enabled."
    p_correction: float
    i_correction: float
    d_correction: float
    speed_multiplier: float
    "The speed multiplier for the robot. This should be a float between -1 and 1. Negative values will make the robot drive backwards."
    error_threshold: float
    degree_offset: int
    gyro_tolerance: int


class HardwareConfig(ConfigBase):
    "The hardware configuration for the robot"

    tire_radius: float
    "The radius of the tire in centimeters"
    brick: "spike.PrimeHub"
    "An instance of the hub API used in the robot"
    gear_selector: "spike.Motor"
    "The motor that selects the attachment gear"
    drive_shaft: "spike.Motor"
    "The motor that drives the robots' attachment gears"
    left_motor: "spike.Motor"
    "The motor that drives the left tire"
    right_motor: "spike.Motor"
    "The motor that drives the right tire"
    driving_motors: "spike.MotorPair"
    "The motor pair that drives the robot. This should be the same as the left and right motors combined."


config = Config()
"The configuration for the robot"
hardware = HardwareConfig()
"The hardware configuration for the robot"

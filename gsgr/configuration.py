import spike
from ._config_base import ConfigBase


class Config(ConfigBase):
    p_correction: float
    i_correction: float
    d_correction: float


class HardwareConfig(ConfigBase):
    tire_radius: float
    brick: spike.PrimeHub
    gear_selector: spike.Motor
    drive_shaft: spike.Motor
    left_motor: spike.Motor
    right_motor: spike.Motor
    driving_motors: spike.MotorPair


config = Config()
hardware = HardwareConfig()

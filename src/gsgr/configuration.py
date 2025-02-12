import typing

import spike

from ._config_base import ConfigBase

if typing.TYPE_CHECKING:
    from .utils import DegreeOMeter


class Config(ConfigBase):
    "Software-Konfiguration für den Roboter"

    debug_mode: bool
    "Ob einige Debug-Funktionen aktiviert sein sollen"
    p_correction: float
    i_correction: float
    d_correction: float
    speed_multiplier: float
    "Der Geschwindigkeitsmultiplikator für den Roboter. Dies sollte eine Fließkommazahl zwischen -1 und 1 sein. Negative Werte lassen den Roboter rückwärts fahren."
    gyro_tolerance: int
    "Die Toleranz bei für den Gyrosensor in Grad, wenn die Gradzahl als Bedingung verwendet wird."
    _degree_o_meter: "DegreeOMeter"
    loop_throttle: float
    "Die Zeit in Sekunden, die zwischen jedem Schleifendurchlauf gewartet werden soll, um den Roboter nicht zu überlasten"


class HardwareConfig(ConfigBase):
    "Hardware-Konfiguration für den Roboter"

    tire_radius: float
    "Der Radradius in cm"
    brick: "spike.PrimeHub"
    "Ein Spike Prime Hub"
    gear_selector: "spike.Motor"
    "Der Motor, der die Getriebe des Roboters steuert"
    drive_shaft: "spike.Motor"
    "Der Motor, der das Getriebe des Roboters antreibt"
    left_motor: "spike.Motor"
    "Der Motor, der das linke Rad antreibt"
    right_motor: "spike.Motor"
    "Der Motor, der das rechte Rad antreibt"
    driving_motors: "spike.MotorPair"
    "Das Motorenpaar, das den Roboter antreibt. Dies sollte das gleiche sein wie die linken und rechten Motoren zusammen."


config = Config()
"The configuration for the robot"
hardware = HardwareConfig()
"The hardware configuration for the robot"

"""Statische Enums"""


class Attachment:
    """Zahnrad-Positionen zur Anseuerung der entsprechenden Ausgänge"""

    FRONT_RIGHT = 180
    FRONT_LEFT = 0
    BACK_RIGHT = 90
    BACK_LEFT = -90


class Pivot:
    """Drehpunkt für GyroTurn"""

    # LEFT_WHEEL_REVERSE = -2
    LEFT_WHEEL = -1
    CENTER = 0
    RIGHT_WHEEL = 1
    # RIGHT_WHEEL_REVERSE = 2


class HWSensor:
    LIGHT = 61


class SWSensor:
    INTEGRATED_LIGHT = 0
    EXTERNAL_LIGHT = 1
    C3PO = 2


class Sensor:
    LIGHT = (HWSensor.LIGHT, SWSensor.INTEGRATED_LIGHT)
    EXTERNAL_LIGHT = (HWSensor.LIGHT, SWSensor.EXTERNAL_LIGHT)
    C3PO = (HWSensor.LIGHT, SWSensor.C3PO)

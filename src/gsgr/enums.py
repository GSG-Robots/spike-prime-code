"""Statische Enums
"""


class Color:
    """SPIKE-Prime Farben"""

    OFF = 0
    PINK = 1
    VIOLET = 2
    BLUE = 3
    TURQUOISE = 4
    LIGHT_GREEN = 5
    GREEN = 6
    YELLOW = 7
    ORANGE = 8
    RED = 9
    WHITE = 10


class Attachment:
    """Zahnrad-Positionen zur Anseuerung der entsprechenden Ausgänge"""

    FRONT_RIGHT = 90
    FRONT_LEFT = -90
    BACK_RIGHT = 0
    BACK_LEFT = 180


class Pivot:
    """Drehpunkt für GyroTurn"""
    
    # LEFT_WHEEL_REVERSE = -2
    LEFT_WHEEL = -1
    CENTER = 0
    RIGHT_WHEEL = 1
    # RIGHT_WHEEL_REVERSE = 2

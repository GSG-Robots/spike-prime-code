import hub
from .configuration import hardware as hw
from micropython import const


_70 = const(70)
_30 = const(30)
_100 = const(100)


chars = {
    "1": ((0, 1, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (1, 1, 1)),
    "2": ((1, 1, 1), (0, 0, 1), (1, 1, 1), (1, 0, 0), (1, 1, 1)),
    "3": ((1, 1, 1), (0, 0, 1), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "4": ((1, 0, 1), (1, 0, 1), (1, 1, 1), (0, 0, 1), (0, 0, 1)),
    "5": ((1, 1, 1), (1, 0, 0), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "6": ((1, 1, 1), (1, 0, 0), (1, 1, 1), (1, 0, 1), (1, 1, 1)),
    "8": ((1, 1, 1), (1, 0, 1), (1, 1, 1), (1, 0, 1), (1, 1, 1)),
    "9": ((1, 1, 1), (1, 0, 1), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "0": ((1, 1, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 1, 1)),
    "x": ((0, 0, 0), (1, 0, 1), (0, 1, 0), (1, 0, 1), (0, 0, 0)),
    "X": ((1, 0, 1), (1, 0, 1), (1, 1, 1), (1, 0, 1), (1, 0, 1)),
    "C": ((1, 1, 1), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 1, 1)),
    "T": ((1, 1, 1), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 0)),
    "R": ((1, 1, 1), (1, 0, 1), (1, 1, 0), (1, 0, 1), (1, 0, 1)),
    "D": ((1, 1, 0), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 1, 0)),
}


def light_up_display(char: int | str, border_right=True, border_left=True, bright=True):
    """Show number on display with styled lines"""

    light = _100 if bright else _70
    dark = _70 if bright else _30

    char = str(char)

    if char in chars:
        hw.brick.light_matrix.off()
        for y, row in enumerate(chars[char]):
            for x, pixel in enumerate(row, 1):
                hw.brick.light_matrix.set_pixel(x, y, pixel * light)
    else:
        raise ValueError("Huh?")
    hw.brick.light_matrix.set_pixel(0, 1, brightness=dark)
    hw.brick.light_matrix.set_pixel(0, 3, brightness=dark)
    hw.brick.light_matrix.set_pixel(4, 1, brightness=dark)
    hw.brick.light_matrix.set_pixel(4, 3, brightness=dark)
    if border_right:
        hw.brick.light_matrix.set_pixel(0, 4, brightness=dark)
        hw.brick.light_matrix.set_pixel(0, 0, brightness=dark)
        hw.brick.light_matrix.set_pixel(0, 2, brightness=dark)
    if border_left:
        hw.brick.light_matrix.set_pixel(4, 0, brightness=dark)
        hw.brick.light_matrix.set_pixel(4, 2, brightness=dark)
        hw.brick.light_matrix.set_pixel(4, 4, brightness=dark)

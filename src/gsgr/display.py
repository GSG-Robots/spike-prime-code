"""Display utils"""

import math

import hub

images = {
    "1": ((0, 1, 0), (1, 1, 0), (0, 1, 0), (0, 1, 0), (1, 1, 1)),
    "2": ((1, 1, 1), (0, 0, 1), (1, 1, 1), (1, 0, 0), (1, 1, 1)),
    "3": ((1, 1, 1), (0, 0, 1), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "4": ((1, 0, 1), (1, 0, 1), (1, 1, 1), (0, 0, 1), (0, 0, 1)),
    "5": ((1, 1, 1), (1, 0, 0), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "6": ((1, 1, 1), (1, 0, 0), (1, 1, 1), (1, 0, 1), (1, 1, 1)),
    "7": ((1, 1, 1), (0, 0, 1), (0, 1, 0), (0, 1, 0), (0, 1, 0)),
    "8": ((1, 1, 1), (1, 0, 1), (1, 1, 1), (1, 0, 1), (1, 1, 1)),
    "9": ((1, 1, 1), (1, 0, 1), (1, 1, 1), (0, 0, 1), (1, 1, 1)),
    "0": ((1, 1, 1), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 1, 1)),
    "x": ((0, 0, 0), (1, 0, 1), (0, 1, 0), (1, 0, 1), (0, 0, 0)),
    "X": ((1, 0, 1), (1, 0, 1), (1, 1, 1), (1, 0, 1), (1, 0, 1)),
    "C": ((1, 1, 1), (1, 0, 0), (1, 0, 0), (1, 0, 0), (1, 1, 1)),
    "T": ((1, 1, 1), (0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 0, 0)),
    "R": ((1, 1, 1), (1, 0, 1), (1, 1, 0), (1, 0, 1), (1, 0, 1)),
    "D": ((1, 1, 0), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 1, 0)),
    "N": ((1, 0, 1), (1, 0.5, 1), (1, 1, 1), (1, 0.5, 1), (1, 0, 1)),
    "J": ((1, 1, 1), (0, 0, 1), (0, 0, 1), (1, 0, 1), (0, 1, 1)),
    "pns": ((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (1, 0, 1)),
    "on": ((1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)),
    "off": ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)),
    "1x1": ((0, 0, 0), (0, 0, 0), (0, 1, 0), (0, 0, 0), (0, 0, 0)),
    "3x3": ((0, 0, 0), (1, 1, 1), (1, 1, 1), (1, 1, 1), (0, 0, 0)),
    "3x3h": ((0, 0, 0), (1, 1, 1), (1, 0, 1), (1, 1, 1), (0, 0, 0)),
    "bat0": ((0, 1, 0), (1, 0, 1), (1, 0, 1), (1, 0, 1), (1, 1, 1)),
    "bat1": ((0, 1, 0), (1, 0, 1), (1, 0, 1), (1, 0.5, 1), (1, 1, 1)),
    "bat2": ((0, 1, 0), (1, 0, 1), (1, 0, 1), (1, 1, 1), (1, 1, 1)),
    "bat3": ((0, 1, 0), (1, 0, 1), (1, 0.5, 1), (1, 1, 1), (1, 1, 1)),
    "bat4": ((0, 1, 0), (1, 0, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)),
    "bat5": ((0, 1, 0), (1, 0.5, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)),
    "bat6": ((0, 1, 0), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)),
}


class Image:
    def __init__(self):
        self.pixels = [0] * 25

    def set_pixel(self, x, y, brightness=100):
        self.pixels[x + y * 5] = brightness

    def show(self):
        hub.light_matrix.show(self.pixels)


def show_image(
    image: (
        int
        | str
        | tuple[
            tuple[int | float, int | float, int | float],
            tuple[int | float, int | float, int | float],
            tuple[int | float, int | float, int | float],
            tuple[int | float, int | float, int | float],
            tuple[int | float, int | float, int | float],
        ]
    ),
    border_right=True,
    border_left=True,
    bright=True,
):
    """Zeigt das angegebene Symbol auf der LED-Matrix an.

    :param border_right: Ob ein Rand auf der rechten Seite angezeigt werden soll, anstatt der beiden Punkte.
    :param border_left: Ob ein Rand auf der linken Seite angezeigt werden soll, anstatt der beiden Punkte.
    :param bright: Ob das Bild in voller Helligkeit angezeigt werden soll.
    """

    img = Image()

    light = 100 if bright else 70
    dark = 40 if bright else 15

    if isinstance(image, int):
        image = str(image)

    if isinstance(image, str):
        if image == "bat":
            i = min(max(math.ceil((hub.battery_voltage() - 7850) / (500 // 7)), 0), 6)
            image = f"bat{i}"
        if image not in images:
            raise ValueError("No image named '%s'" % image)
        image = images[image]

    if isinstance(image, tuple):
        for y, row in enumerate(image):
            for x, pixel in enumerate(row, 1):
                img.set_pixel(x, y, round(pixel * light))
    else:
        raise TypeError("Image cannot be rendered, invalid type")

    img.set_pixel(0, 1, dark)
    img.set_pixel(0, 3, dark)
    img.set_pixel(4, 1, dark)
    img.set_pixel(4, 3, dark)

    if border_right:
        img.set_pixel(0, 4, dark)
        img.set_pixel(0, 0, dark)
        img.set_pixel(0, 2, dark)
    if border_left:
        img.set_pixel(4, 4, dark)
        img.set_pixel(4, 0, dark)
        img.set_pixel(4, 2, dark)

    img.show()

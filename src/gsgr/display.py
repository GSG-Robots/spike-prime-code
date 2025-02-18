"""Display utils
"""

import hub
from micropython import const

images: dict[
    str,
    tuple[
        tuple[int, int, int],
        tuple[int, int, int],
        tuple[int, int, int],
        tuple[int, int, int],
        tuple[int, int, int],
    ],
] = const(
    {
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
        "N": ((1, 0, 1), (1, 0.5, 1), (1, 1, 1), (1, 0.5, 1), (1, 0, 1)),
        "J": ((1, 1, 1), (0, 0, 1), (0, 0, 1), (1, 0, 1), (0, 1, 1)),
        "pns": ((0, 1, 0), (0, 1, 0), (0, 1, 0), (0, 1, 0), (1, 0, 1)),
        "on": ((1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1), (1, 1, 1)),
        "off": ((0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0), (0, 0, 0)),
    }
)


def show_image(
    image: (
        int
        | str
        | tuple[
            tuple[int, int, int],
            tuple[int, int, int],
            tuple[int, int, int],
            tuple[int, int, int],
            tuple[int, int, int],
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

    img = hub.Image(5, 5)

    light = 9 if bright else 7
    dark = 7 if bright else 3

    if isinstance(image, int):
        image = str(image)

    if isinstance(image, str):
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

    hub.display.show(img)

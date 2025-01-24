"""Display utils
"""

from micropython import const

from .configuration import hardware as hw


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
    """Show given symbol on light matrix.

    :param border_right: Whether to display a border on the right, rather than the two dots.
    :param border_left: Whether to display a border on the left, rather than the two dots.
    :param bright: Whether to display at full brightness.
    """

    light = 100 if bright else 70
    dark = 70 if bright else 30

    if isinstance(image, int):
        image = str(image)

    if isinstance(image, str):
        if image not in images:
            raise ValueError("No image named '%s'" % image)
        image = images[image]

    if isinstance(image, tuple):
        hw.brick.light_matrix.off()
        for y, row in enumerate(image):
            for x, pixel in enumerate(row, 1):
                hw.brick.light_matrix.set_pixel(x, y, int(pixel * light))
    else:
        raise TypeError("Image cannot be rendered, invalid type")

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

# LEGO type:standard slot:4 autostart

import time
from spike import PrimeHub


void = lambda *_, **__: None


class ChainedFunction(list):
    def __call__(self, *args, **kwargs):
        for func in self:
            func(*args, **kwargs)


class OptionalChainedFunction(ChainedFunction):
    func = None

    def add(self, func):
        if self.func is None:
            self.func = func
        else:
            if not isinstance(self.func, ChainedFunction):
                self.func = ChainedFunction()

            self.func.append(func)

    def __call__(self, *args, **kwargs):
        if self.func:
            self.func(*args, **kwargs)


class Check:
    def __init__(self) -> None:
        self.setup = ChainedFunction()
        self.check = ChainedFunction()
        self.cleanup = ChainedFunction()

    def on_setup(self, func) -> "Check":
        self.setup.append(func)
        return self

    def on_check(self, func) -> "Check":
        self.check.append(func)
        return self

    def on_cleanup(self, func) -> "Check":
        self.cleanup.append(func)
        return self


class Brightness:
    OFF = 0
    VERYLOW = 1
    LOW = 2
    MEDIUM = 3
    HIGH = 4
    VERYHIGH = 5
    FULL = 6
    ON = 7

    _STEPS = [0, 20, 40, 50, 60, 75, 90, 100]


class Image:
    image: int = 0b0

    def set_pixel(self, x: int, y: int, brightness: int = Brightness.ON) -> "Image":
        if not isinstance(x, int):
            raise TypeError("x must be int")
        if not isinstance(y, int):
            raise TypeError("y must be int")
        if not 0 <= x <= 4:
            raise ValueError("x must be between 0 and 4")
        if not 0 <= y <= 4:
            raise ValueError("y must be between 0 and 4")
        if not 0 <= brightness <= 7:
            raise ValueError(
                "brightness must be between 0 (Brighness.OFF) and 7 (Brightness.ON)"
            )

        x = 4 - x
        y = 4 - y

        self.image = self.image & (0b111 << (3 * (x + 5 * y))) | (
            brightness << (3 * (x + 5 * y))
        )

        return self

    def set_row(self, row: int, brightness: int = Brightness.ON) -> "Image":
        if not isinstance(row, int):
            raise TypeError("row must be int")
        if not 0 <= row <= 0b111_111_111_111_111:
            raise ValueError("row must be between 0 and 7")
        if not 0 <= brightness <= 7:
            raise ValueError(
                "brightness must be between 0 (Brighness.OFF) and 7 (Brightness.ON)"
            )
        row = 4 - row
        self.image = self.image & (0b000_000_000_000_000 << (15 * row)) | (
            brightness << (15 * row)
        )
        return self

    def append_top(self, row: int) -> "Image":
        if not isinstance(row, int):
            raise TypeError("row must be int")
        if not 0 <= row <= 0b111_111_111_111_111:
            raise ValueError("row must be between 0 and 7")
        self.image = self.image >> 15 | (row << 15)

    def append_bottom(self, row: int) -> "Image":
        if not isinstance(row, int):
            raise TypeError("row must be int")
        if not 0 <= row <= 0b111_111_111_111_111:
            raise ValueError("row must be between 0 and 7")
        self.image = self.image << 15 | row

    def get_pixel(self, x: int, y: int) -> int:
        if not 0 <= x <= 4:
            raise ValueError("x must be between 0 and 4")
        if not 0 <= y <= 4:
            raise ValueError("y must be between 0 and 4")
        x = 4 - x
        y = 4 - y
        return self.image >> (3 * (x + 5 * y)) & 0b111

    def get_row(self, row: int) -> int:
        if not 0 <= row <= 4:
            raise ValueError("row must be between 0 and 4")
        return self.image >> (15 * (4 - row)) & 0b111_111_111_111_111

    def get_column(self, column: int) -> int:
        if not 0 <= column <= 4:
            raise ValueError("column must be between 0 and 4")
        result = 0
        for row in range(5):
            result |= (self.image >> (3 * (4 - row)) & 0b111) << (3 * row)
        return result

    def get_int(self) -> int:
        if (
            not 0
            <= self.image
            <= 0b111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111_111
        ):
            raise RuntimeError(
                "Image.image must be between 0 and 37778931862957161709567"
            )
        return self.image

    def __repr__(self):
        return bin(self.image)


class Brick:
    def __init__(self):
        self.current_image = 0b0
        self.brick = PrimeHub()

    def draw_image(self, image: Image):
        if not isinstance(image, Image):
            raise TypeError("image must be of type Image")

        image_int = image.get_int()

        for z in range(25):
            x = 4 - z // 5
            y = 4 - z % 5
            self.brick.light_matrix.set_pixel(y, x, Brightness._STEPS[image_int & 7])
            image_int >>= 3


brick = Brick()

image = Image()
image.set_pixel(1, 1, Brightness.ON)
brick.draw_image(image)

time.sleep(1)

image.append_top(0b000_000_000_000_000)
brick.draw_image(image)
time.sleep(1)

image.append_bottom(0b000_111_000_111_000)
brick.draw_image(image)

print(bin(image.get_pixel(1, 1)))
print(bin(image.get_row(1)))
print(bin(image.get_column(1)))

time.sleep(1)

image.set_row(0, Brightness.ON)
brick.draw_image(image)
print(bin(image.get_row(0)))

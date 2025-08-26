from typing import Callable, overload


class Button:
    def is_pressed(self): ...
    def was_pressed(self): ...
    @overload
    def callback(self, function: Callable[[int], None]) -> None:...
    @overload
    def callback(self) -> Callable[[int], None]:...

left: Button
right: Button
center: Button
connect: Button

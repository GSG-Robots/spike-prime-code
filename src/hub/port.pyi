from typing import Any, Callable, Iterable, overload, BinaryIO

DETACHED = 0
ATTACHED = 1

MODE_DEFAULT = 0
MODE_FULL_DUPLEX = 1
MODE_HALF_DUPLEX = 2
MODE_GPIO = 3

class Device:
    FORMAT_RAW = 0
    FORMAT_PCT = 1
    FORMAT_SI = 2

    @overload
    def mode(self, mode: int, data: bytes | None = None): ...
    @overload
    def mode(self, mode: tuple[int, int], data: bytes | None = None): ...
    @overload
    def mode(self, mode: Iterable[tuple[int, int]], data: bytes | None = None): ...
    def get(self, format: int | None = None) -> tuple[int, ...]: ...
    def pwm(self, duty_cycle: int) -> None: ...

class Motor(Device):
    BUSY_MODE = 0
    BUSY_MOTOR = 1

    STOP_FLOAT = 0
    STOP_BRAKE = 1
    STOP_HOLD = 2

    EVENT_COMPLETED = 0
    EVENT_INTERRUPTED = 1
    EVENT_STALLED = 2

    @overload
    def default(self) -> dict[str, Any]: ...
    @overload
    def default(
        self,
        pid: tuple[int, int, int] = (0, 0, 0),
        max_power: int = 0,
        speed: int | float = 0,
        stall: bool = True,
        deceleration: int = 150,
        stop: int = 1,
        callback: Callable[[int], None] = lambda x: None,
        acceleration: int = 100,
    ) -> dict[str, Any] | None: ...
    def pair(self, other_motor: Motor) -> MotorPair: ...
    @overload
    def callback(self) -> Callable[[int], None] | None: ...
    @overload
    def callback(self, function: Callable[[int], None] | None) -> None: ...
    def preset(self, position: int): ...
    @overload
    def pid(self, p: int | float, i: int | float, d: int | float) -> None: ...
    @overload
    def pid(self) -> tuple[float, float, float]: ...
    def busy(self, type: int) -> bool: ...
    def run_at_speed(
        self,
        speed: int | float,
        *,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stall: bool | None = None,
    ) -> None: ...
    def run_for_time(
        self,
        msec: int | float,
        *,
        speed: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stall: bool | None = None,
        stop: int | None = None,
    ) -> None: ...
    def run_for_degrees(
        self,
        degrees: int | float,
        *,
        speed: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stall: bool | None = None,
        stop: int | None = None,
    ) -> None: ...
    def run_to_position(
        self,
        position: int,
        *,
        speed: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stall: bool | None = None,
        stop: int | None = None,
    ) -> None: ...
    def brake(self) -> None: ...
    def hold(self) -> None: ...
    def float(self) -> None: ...

class MotorPair:
    def id(self) -> int: ...
    def primary(self) -> Motor: ...
    def secondary(self) -> Motor: ...
    def unpair(self) -> bool: ...
    def brake(self) -> None: ...
    def hold(self) -> None: ...
    def float(self) -> None: ...
    def pwm(self, pwm_0: int, pwm_1: int) -> None: ...
    def run_at_speed(
        self,
        speed_0: int,
        speed_1: int,
        *,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
    ) -> None: ...
    def run_for_time(
        self,
        msec: int,
        *,
        speed_0: int | float | None = None,
        speed_1: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stop: int | None = None,
    ) -> None: ...
    def run_for_degrees(
        self,
        degrees: int,
        *,
        speed_0: int | float | None = None,
        speed_1: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stop: int | None = None,
    ) -> None: ...
    def run_to_position(
        self,
        position_0: int,
        position_1: int,
        *,
        speed: int | float | None = None,
        max_power: int | None = None,
        acceleration: int | None = None,
        deceleration: int | None = None,
        stop: int | None = None,
    ) -> None: ...
    def preset(self, position_0: int, position_1: int) -> None: ...
    def pid(self, p: int | float, i: int | float, d: int | float) -> None: ...
    @overload
    def callback(self) -> Callable[[int], None] | None: ...
    @overload
    def callback(self, function: Callable[[int], None] | None) -> None: ...

class Pin:
    @overload
    def direction(self, direction: int) -> None: ...
    @overload
    def direction(self) -> int: ...
    @overload
    def value(self, value: int) -> None: ...
    @overload
    def value(self) -> int: ...

class Port:
    motor: Motor = Motor()
    device: Device = Device()

    p5: Pin
    p6: Pin

    def mode(self, mode: int, baud_rate: int = 2400) -> None: ...
    def pwm(self, value: int) -> None:
        """
        Applies a PWM signal to the power pins of the port or device.

        A PWM value of 0 has the same effect as .float()

        :param value: PWM value between -100 and 100. The polarity of the
                      PWM signal mathces the sign of the value. A value of 0 stops
                      the PWM signal and leaves the port driver in the floating state.
        """

    def callback(self, function: Callable[[int], None]) -> None:
        """Sets the callback function that is called when a device is plugged into
        the port or unplugged from the port.

        The function must accept one argument, which indicates why the callback was called.
        See the port constants for all possible values.

        :param function: Callable function that takes one argument.
                         Choose :py:`None` to disable the callback.
        """

    def info(self) -> dict[str, Any]: ...
    def baud(self, baus: int) -> None: ...
    @overload
    def read(self, read: int) -> int: ...
    @overload
    def read(self, read: BinaryIO) -> int: ...
    def write(self, write: bytes) -> int: ...

A = Port()
B = Port()
C = Port()
D = Port()
E = Port()
F = Port()

__all__ = [
    "ATTACHED",
    "DETACHED",
    "MODE_DEFAULT",
    "MODE_FULL_DUPLEX",
    "MODE_HALF_DUPLEX",
    "MODE_GPIO",
    "A",
    "B",
    "C",
    "D",
    "E",
    "F",
]

from typing import Callable


class _Motor: ...


class _Port:
    motor: _Motor

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


A = _Port()
B = _Port()
C = _Port()
D = _Port()
E = _Port()
F = _Port()

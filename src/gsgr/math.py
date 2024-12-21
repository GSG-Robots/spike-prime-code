"""Some basic math utility functions."""
import math


def sigmoid(x: float) -> float:
    """Implementatuion of :wikipedia:`Sigmoid function`

    :param x: function parameter x
    """
    return (1 + math.tanh(x / 2)) * 0.5


def clamp(value: float | int, minimum: float | int, maximum: float | int) -> float:
    """Helper function to ensure a number is in a a given range.
    
    :param value: Value to min-max / clamp.
    :param minimum: minimum value for :py:obj:`value`.
    :param maximum: maximum value for :py:obj:`value`.
    
    :returns: :py:obj:`minimum` if :py:obj:`value` is below :py:obj:`minimum`
    :returns: :py:obj:`maximum` if :py:obj:`value` is above :py:obj:`maximum`
    :returns: :py:obj:`value` if :py:obj:`value` is between :py:obj:`minimum` and :py:obj:`maximum`
    """
    return float(max(minimum, min(value, maximum)))

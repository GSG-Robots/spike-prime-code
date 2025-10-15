"""Grundlegende Mathematische Funktionen und Hilfsfunktionen"""

import math


def sigmoid(x: float) -> float:
    """Implementation der :wikipedia:`Sigmoid Funktion`

    :param x: Funktions Parameter x
    """
    return (1 + math.tanh(x / 2)) * 0.5


def clamp(value: float, minimum: float, maximum: float) -> float:
    """Hilfsfunktion, um sicherzustellen, dass sich eine Zahl in dem angegebenen Bereich befindet.

    :param value: Zahl, die ge-min-max-t werden soll.
    :param minimum: Untergrenze für :py:obj:`value`.
    :param maximum: Obergrenze für :py:obj:`value`.

    :returns: :py:obj:`minimum`, wenn :py:obj:`value` unter :py:obj:`minimum` liegt
    :returns: :py:obj:`maximum`, wenn :py:obj:`value` über :py:obj:`maximum` liegt
    :returns: :py:obj:`value`, wenn :py:obj:`value` zwischen :py:obj:`minimum` und :py:obj:`maximum` liegt
    """
    return float(max(minimum, min(value, maximum)))

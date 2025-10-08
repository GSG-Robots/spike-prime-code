"""Basic conditions"""

from .types import Condition

def static(value: bool | int, /) -> Condition:
    """Statische Bedingung. Dauerhaft entweder erfüllt oder nicht erfüllt.

    :param value: :py:obj:`True` bedeutet, dass die Bedingung dauerhaft erfüllt ist, :py:obj:`False` das Gegenteil.
    """

def cm(distance: int | float, /) -> Condition:
    """... bis sich die Räder um eine Bestimmte Strecke bewegt haben.

    :param distance: Die Strecke, die zurückgelegt werden soll, in cm.
    """

def sec(duration: int | float, /) -> Condition:
    """... bis eine bestimmte Zeit vergangen ist.

    :param duration: Die Dauer, die gewartet werden soll, in Sekunden.
    """

def impact(during: Condition, /, threshold: int | float = 500, min: int = 50) -> Condition: ...
def pickup(during: Condition, /, threshold: int | float = 500, min: int = 50) -> Condition: ...
def deg(angle: int, /) -> Condition:
    """... bis der Roboter in eine bestimmte Richtung gedreht hat.

    :param angle: Der Winkel, in den der Roboter relativ zum Origin gedreht sein soll.
    """

def light_left(threshold: float, below: bool = False): ...
def light_right(threshold: float, below: bool = False): ...
def THEN(first: Condition, second: Condition, /) -> Condition:
    """... bis eine Bedingung erfüllt ist, und dann noch eine andere.

    Dabei werden die beiden Bedingungen nacheinander ausgeführt. :py:obj:`THEN(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(8)`

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """

def OR(first: Condition, second: Condition, /) -> Condition:
    """... bis eine von zwei Bedingungen erfüllt ist.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis mindestens eine erfüllt ist. :py:obj:`OR(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(3)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """

def AND(first: Condition, second: Condition, /) -> Condition:
    """... bis beide von zwei Bedingungen erfüllt sind.

    Dabei werden die beiden Bedingungen gleichzeitig ausgeführt, bis beide erfüllt sind. :py:obj:`AND(cm(3), cm(5))` wird also das gleiche Ergebnis haben wie :py:obj:`cm(5)`.

    :param first: Die erste Bedingung, die erfüllt werden soll.
    :param second: Die zweite Bedingung, die erfüllt werden soll.
    """

def NOT(cond: Condition, /) -> Condition:
    """... bis eine Bedingung nicht erfüllt ist.

    :param cond: Die Bedingung, die nicht erfüllt sein soll.
    """

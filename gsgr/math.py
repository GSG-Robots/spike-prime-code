import math


def sigmoid(x: float) -> float:
    return (1 + math.tanh(x / 2)) * 0.5


def clamp(value: float | int, minimum: float | int, maximum: float | int) -> float:
    return float(max(minimum, min(value, maximum)))

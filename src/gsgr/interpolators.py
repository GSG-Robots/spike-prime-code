def linear(start: float, end: float, t: float) -> float:
    return (1 - t) * start + t * end


def exponential(start: float, end: float, t: float) -> float:
    if start == 0:
        return end * t
    if end == 0:
        return start * (1 - t)
    return start * ((end / start) ** t)

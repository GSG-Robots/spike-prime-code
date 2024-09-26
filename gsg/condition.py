import math
from .config import config

class EndingCondition:
    """Ending Condition: Infinite and Base for other Ending Conditions"""

    def check(self, run):
        # this ugly thing is used because pylint wants me to use the run arg.
        return not bool(run)
    
    def __invert__(self):
        return _Invert(self)

    def __or__(self, other):
        return _OrCond(self, other)

    def __ror__(self, other):
        return _OrCond(self, other)

    def __and__(self, other):
        return _AndCond(self, other)

    def __rand__(self, other):
        return _AndCond(self, other)


class _OrCond(EndingCondition):
    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) or self.condition_b.check(run)


class _AndCond(EndingCondition):
    def __init__(
        self, condition_a: EndingCondition, condition_b: EndingCondition
    ) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) and self.condition_b.check(run)


class _Invert(EndingCondition):
    def __init__(self, condition: EndingCondition) -> None:
        self.condition = condition

    def check(self, run):
        return not self.condition.check(run)

class Cm(EndingCondition):
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return (
            (
                abs(run.right_motor.get_degrees_counted())
                + abs(run.left_motor.get_degrees_counted())
            )
            / 360
            * math.pi
            * run.tire_radius
        ) >= self.value


class Sec(EndingCondition):
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return run.timer.now() >= self.value


class Line(EndingCondition):
    def check(self, run):
        return (
            run.front_light_sensor.get_reflected_light() < run.light_black_value + 5
            or run.back_light_sensor.get_reflected_light() < run.light_black_value + 5
        )


class Deg(EndingCondition):
    def __init__(self, value: int) -> None:
        self.value = value

    def check(self, run):
        return (
            self.value - run.turning_degree_tolerance
            <= run.brick.motion_sensor.get_yaw_angle()
            <= self.value + run.turning_degree_tolerance
        )

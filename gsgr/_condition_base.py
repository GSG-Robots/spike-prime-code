import math
from .configuration import config


class ConditionBase:
    """Ending Condition: Infinite and Base for other Ending Conditions"""

    def setup(self, run):
        ...

    def check(self, run):
        return False

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


class _OrCond(ConditionBase):
    def __init__(self, condition_a: ConditionBase, condition_b: ConditionBase) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) or self.condition_b.check(run)


class _AndCond(ConditionBase):
    def __init__(self, condition_a: ConditionBase, condition_b: ConditionBase) -> None:
        self.condition_a = condition_a
        self.condition_b = condition_b

    def check(self, run):
        return self.condition_a.check(run) and self.condition_b.check(run)


class _Invert(ConditionBase):
    def __init__(self, condition: ConditionBase) -> None:
        self.condition = condition

    def check(self, run):
        return not self.condition.check(run)

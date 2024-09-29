from typing import Any

from .task import Task
from .yieldable_exc import YieldableExcercise

__all__ = ["SusyncFunction", "is_susync"]
_GT = type((lambda: (yield))())


class SusyncFunction:
    def __init__(self, func, name=None):
        self._target = func
        self.__name__ = name or func.__name__

    def _ensure_generates(self, *args, **kwargs):
        yield YieldableExcercise(lambda task: ...)
        generator = self._target(*args, **kwargs)
        if isinstance(generator, _GT):
            yield from generator
        else:
            # print(f"Warning: {self.__name__} is an susync function, but does not yield.")
            return generator

    def _get_prepared_generator(self, *args, **kwargs):
        generator = self._ensure_generates(*args, **kwargs)
        next(generator)
        return generator

    def make_task(self, *args, **kwargs):
        return Task(self.__name__, self._get_prepared_generator(*args, **kwargs))

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        return self.make_task(*args, **kwargs)


def is_susync(func):
    return isinstance(func, SusyncFunction)

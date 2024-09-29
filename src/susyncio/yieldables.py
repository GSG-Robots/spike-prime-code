import time

from .helpers import yieldable

__all__ = ["freeze", "skip"]


@yieldable
def freeze(task, seconds):
    return time.sleep(seconds)


@yieldable
def skip(task): ...

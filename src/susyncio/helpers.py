from typing import Callable

from .logic import STATE, EventLoop
from .susync_func import SusyncFunction
from .task import Task
from .yieldable_exc import YieldableExcercise

__all__ = [
    "run",
    "create_task",
    "yieldable",
    "on",
    "once",
    "fire",
    "get_loop",
    "susync",
]


def susync(func):
    return SusyncFunction(func, name=func.__name__)


def get_loop() -> EventLoop:
    return STATE.get_loop()


def run(task: Task):
    loop = get_loop()
    loop.add_task(task)
    loop.run_until_complete()


def create_task(func):
    loop = get_loop()
    loop.add_task(func)


def yieldable(func):
    return lambda *args, **kwargs: YieldableExcercise(
        lambda task: func(task, *args, **kwargs)
    )


def on(event: str, callback: Callable | None = None):
    loop = get_loop()
    return loop.on(event, callback)


def once(event: str, callback: Callable | None = None):
    loop = get_loop()
    return loop.once(event, callback)


def fire(event: str, *args, **kwargs):
    loop = get_loop()
    loop.fire(event, *args, **kwargs)

import time

from .helpers import get_loop, susync
from .task import Task
from .yieldable_exc import YieldableExcercise
from .yieldables import skip

__all__ = ["sleep", "gather"]


@susync
def sleep(seconds):
    start_time = time.time()
    while time.time() - start_time < seconds:
        yield skip()


@susync
def gather(*tasks: Task):
    for task in tasks:
        get_loop().add_task(task)
    while any(task.is_alive for task in tasks):
        yield skip()
    if any(task.has_failed for task in tasks):
        raise RuntimeError("Some tasks have failed while gathering.")
    if any(task.was_cancelled for task in tasks):
        raise RuntimeError("Some tasks have been cancelled while gathering.")
    return [task.result for task in tasks]
    # raise StopIteration([task.result for task in tasks])


# @susync
# def gather(*tasks: Task):
#     return run_all_tasks(get_loop(), list(tasks))


@susync
def send_yieldable(excercise: YieldableExcercise):
    yield excercise

from typing import Optional

from .events import EventSystem
from .task import Task

__all__ = ["EventLoop", "STATE"]


class EventLoop(EventSystem):
    def __init__(self: "EventLoop"):
        super().__init__(self)
        self._tasks: list[Task] = []

    def tick(self):
        cptasks = self._tasks.copy()
        for task in cptasks:
            task._loop = self
            if not isinstance(task, Task):
                raise RuntimeError("A task is not a Task instance:", task)
            try:
                next(task)
            except StopIteration:
                self._tasks.remove(task)

    def run_until_complete(self):
        if STATE.get_loop() is not self:
            raise RuntimeError("This loop is not the main loop")
        while self._tasks:
            self.tick()

    def add_task(self, task: Task) -> Task:
        self._tasks.append(task)
        return task


class _StatePublicInterface:
    class _State:
        main_loop: Optional[EventLoop] = None

    __state: _State = _State()

    def get_loop(self):
        if self.__state.main_loop is None:
            self.__state.main_loop = EventLoop()
        return self.__state.main_loop


STATE = _StatePublicInterface()

__all__ = ["Task"]

from .exceptions import TickingStoppedTask
from .yieldable_exc import YieldableExcercise

_TC = 0


class State:
    IDLE = 0
    STARTED = 1
    FINISHED = 2
    CANCELLED = 3
    FAILED = 4


class Task:
    def __init__(self, name, generator):
        self.name = name
        self._loop = None
        self._generator = generator
        self._state = State.IDLE
        self._marked_as_cancelled = False
        self._value = None
        global _TC
        self.id = _TC
        _TC += 1

    @property
    def was_started(self):
        return self._state >= State.STARTED

    @property
    def was_cancelled(self):
        return self._state == State.CANCELLED

    @property
    def has_failed(self):
        return self._state == State.FAILED

    @property
    def has_finished(self):
        return self._state == State.FINISHED

    @property
    def is_alive(self):
        return self._state < State.FINISHED

    @property
    def result(self):
        if self._state == State.FINISHED:
            return self._value
        raise AttributeError("Task has not finished")

    @property
    def exception(self):
        if self._state == State.FAILED:
            return self._value
        raise AttributeError("Task has not failed")

    def cancel(self):
        self._marked_as_cancelled = True

    def _set_state(self, state, value=None):
        self._state = state
        self._value = value

    def _fail(self, exception):
        self._set_state(State.FAILED, exception)

    def __id__(self):
        return self.id

    def __iter__(self):
        return self

    def __next__(self):
        if not self.was_started:
            self._set_state(State.STARTED)
        if self._marked_as_cancelled:
            self._set_state(State.CANCELLED)
            self._marked_as_cancelled = False
            raise StopIteration()
        if not self.is_alive:
            raise TickingStoppedTask(self.name)
        try:
            yieldable = next(self._generator)
            # print(yieldable, self.name)
            if yieldable is None:
                return
            if not isinstance(yieldable, YieldableExcercise):
                raise RuntimeError(
                    "A task yielded something that is not a YieldableExcercise. Note: You cannot use iterators with susyncio."
                )
            yieldable.func(self)
        except StopIteration as e:
            print("finished", self.name, e.value)
            self._set_state(State.FINISHED, e.value)
            raise e
        except Exception as e:
            self._fail(e)
            raise e

    def __del__(self):
        if not self.was_started:
            e = RuntimeError(
                f"A task was created but never started. Missing `await` or `yield from`? Task: {self.name}"
            )
            raise e
        if self.is_alive:
            print(self._state)
            e = RuntimeError(
                f"A task was started but never finished. The generator was not fully consumed. Task: {self.name}"
            )
            raise e

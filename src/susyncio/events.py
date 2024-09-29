from typing import TYPE_CHECKING, Any, Callable

from .susync_func import is_susync

if TYPE_CHECKING:
    from .logic import EventLoop


class EventSystem:
    def __init__(self, loop: "EventLoop"):
        self._loop = loop
        self._event_handlers: dict[str, list[Callable[..., Any]]] = {}

    def on(self, event: str, callback: Callable | None = None):
        if callback is None:
            return lambda callback: self.on(event, callback)
        if event not in self._event_handlers:
            self._event_handlers[event] = []
        self._event_handlers[event].append(callback)

    def once(self, event: str, callback: Callable | None = None):
        if callback is None:
            return lambda callback: self.once(event, callback)

        def wrapper(*args, **kwargs):
            callback(*args, **kwargs)
            self.remove_handler(event, wrapper)

        self.on(event, wrapper)

    def fire(self, event: str, *args, **kwargs):
        for handler in self._event_handlers.get(event, []):
            if is_susync(handler):
                self._loop.add_task(handler(*args, **kwargs))
            else:
                handler(*args, **kwargs)

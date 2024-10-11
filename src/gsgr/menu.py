from spike import Motor
from .display import light_up_display
from .exceptions import ExitMenu, StopRun
from .configuration import hardware as hw, config as cnf
from .math import clamp


class MenuItem:
    def __init__(self, display_as: int | str, color: str = "white") -> None:
        self.display_as = display_as
        self.color = color
        self.callback = lambda: ...

    def get_callback(self):
        return self.callback

    def set_callback(self, func=None):
        def decorator(func):
            self.callback = func
            return func

        if func:
            return decorator(func)
        return decorator

    def cleanup(self): ...

    def stop(self):
        raise StopRun


class Run(MenuItem):
    def __init__(self, display_as, color, config, run):
        super().__init__(display_as, color)
        self.context = config or cnf()
        self.set_callback(run)

    def get_callback(self):
        self.context.__enter__()
        return super().get_callback()

    def cleanup(self):
        for port in ("A", "B", "C", "D", "E", "F"):
            try:
                Motor(port).stop()
            except KeyboardInterrupt:
                ...
        self.context.__exit__(None, None, None)


class Menu:
    def __init__(self, items: list[MenuItem] | None = None, landscape=False):
        self.items = items or []
        self.landscape = landscape
        self.position = 0

    def add_item(self, item: MenuItem):
        self.items.append(item)

    def get(self):
        last_position = -1
        try:
            while True:
                if hw.brick.left_button.was_pressed():
                    self.position = self.position - (-1 if self.landscape else 1)
                if hw.brick.right_button.was_pressed():
                    self.position = self.position + (-1 if self.landscape else 1)

                self.position = int(clamp(self.position, 0, len(self.items) - 1))

                if last_position != self.position:
                    light_up_display(
                        self.items[self.position].display_as,
                        self.position == 0,
                        self.position == (len(self.items) - 1),
                        True,
                    )
                    hw.brick.status_light.on(self.items[self.position].color)
                    last_position = self.position

        except (KeyboardInterrupt, SystemExit):
            return self.items[self.position]

    def loop(self, autoscroll=False):
        while True:
            result = self.get()
            light_up_display(result.display_as, True, True, False)
            try:
                callback = result.get_callback()
                callback()
                result.cleanup()
            except KeyboardInterrupt:
                result.cleanup()
                continue
            except ExitMenu:
                result.cleanup()
                break

            if autoscroll:
                self.position += 1

    def exit(self):
        raise ExitMenu

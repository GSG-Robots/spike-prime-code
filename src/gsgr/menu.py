"""Module for menu management.

Also supplies run class, being a menu item.
"""

from typing import Callable, ContextManager
from spike import Motor

from .configuration import config as cnf
from .configuration import hardware as hw
from .display import light_up_display
from .exceptions import ExitMenu, StopRun
from .math import clamp


class MenuItem:
    display_as: int | str
    """Character or digit to display in menu, indicating which menu item is selected."""
    color: str
    """Color of the status light to indicate which menu item is selected."""
    callback: Callable
    """Function to call when menu item is selected."""

    def __init__(self, display_as: int | str, color: str = "white") -> None:
        """
        :param display_as: Charackter or digit to display in menu, indicating which menu item is selected. Sets :py:attr:`display_as` initially.
        :param color: Color of the status light to indicate which menu item is selected. Sets :py:attr:`color` initially. Defaults to `"white"`.
        """
        self.display_as = display_as
        self.color = color
        self.callback = lambda: ...

    def get_callback(self) -> Callable:
        """Getter function for :py:attr:`callback`."""
        return self.callback

    def set_callback(self, func: Callable | None = None):
        """Setter function for :py:attr:`callback`.

        :param func: Function to set as callback. If not provided, returns a decorator function. Defaults to `None`.
        """

        def decorator(func):
            self.callback = func
            return func

        if func:
            return decorator(func)
        return decorator

    def cleanup(self):
        """Funtion called after menu item callback has finished."""

    def stop(self):
        """Helper function to stop the callback function of a :py:class:`~gsgr.menu.MenuItem`.

        :raises: :py:class:`~gsgr.exceptions.StopRun`
        """
        raise StopRun


class Run(MenuItem):
    context: ContextManager
    """A context manager in which the run is being executed.
    
    This is implemented to support :py:class:`~gsgr.configuration.Config` changes for individual runs.
    """

    def __init__(
        self,
        display_as: int | str,
        color: str,
        config: ContextManager | None,
        run: Callable,
    ):
        """
        :param display_as: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`display_as` initially.
        :param color: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`color` initially.
        :param config: A context manager to execute the run in. Designed for :py:class:`~gsgr.configuration.Config` calls. Sets :py:attr:`context` initially.
        """
        super().__init__(display_as, color)
        self.context = config or cnf()
        self.set_callback(run)

    def get_callback(self):
        """Patched verison of :py:meth:`MenuItem.get_callback` to enter the context manager / loading run specific config before returning the callback."""
        self.context.__enter__()
        return super().get_callback()

    def cleanup(self):
        """Stop all motors and exit the context manager. This means resetting the config."""
        for port in ("A", "B", "C", "D", "E", "F"):
            try:
                Motor(port).stop()
            except RuntimeError:
                ...
        self.context.__exit__(None, None, None)


class Menu:
    """A general menu holding :py:class:`~gsgr.menu.MenuItem` s"""

    items: list[MenuItem]
    """A list of all :py:class:`~gsgr.menu.MenuItem` s in the menu"""

    landscape: bool
    """Whether controls are optimized for landscape usage"""

    position: int
    """Currently displayed menu item index"""

    def __init__(self, items: list[MenuItem] | None = None, landscape=False):
        """
        :param items: a list of :py:class:`~gsgr.menu.MenuItem` s to be included initially. Defaults to an empty list.
        :param landscape: whether to optimize controls for landscape mode. Defaults to False.
        """
        self.items = items or []
        self.landscape = landscape
        self.position = 0

    def add_item(self, item: MenuItem):
        """Helper function to append an item to the menu

        :param item: Item to append
        """
        self.items.append(item)

    def get(self) -> MenuItem:
        """Show menu and allow to select item

        :returns: the selected item
        """
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
        """Show the menu and run the callback of the selected item in an infinite loop.

        :param autoscroll: whether to scroll to the next item after executing the callback of a :py:class:`~gsgr.menu.MenuItem` automatically.
        """
        while True:
            result = self.get()
            light_up_display(result.display_as, True, True, False)
            try:
                callback = result.get_callback()
                try:
                    callback()
                except Exception as e:
                    if cnf.debug_mode:
                        hw.brick.light_matrix.write(type(e).__name__ + ":" + str(e))
                    raise e
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
        """Helper function to exit :py:meth:`~gsgr.menu.Menu.loop`.

        :raises: ExitMenu
        """
        raise ExitMenu

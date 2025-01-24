"""Module for menu management.

Also supplies run class, being a menu item.
"""

from typing import Callable

from .configuration import config as cnf
from .configuration import hardware as hw
from .display import show_image
from .exceptions import ExitMenu, StopRun
from .math import clamp


class MenuItem:
    display_as: int | str
    """Character or digit to display in menu, indicating which menu item is selected."""
    color: str
    """Color of the status light to indicate which menu item is selected."""

    def __init__(self, display_as: int | str, color: str = "white") -> None:
        """
        :param display_as: Charackter or digit to display in menu, indicating which menu item is selected. Sets :py:attr:`display_as` initially.
        :param color: Color of the status light to indicate which menu item is selected. Sets :py:attr:`color` initially. Defaults to `"white"`.
        """
        self.display_as = display_as
        self.color = color


class ActionMenuItem(MenuItem):
    action: Callable | None
    """Function to call when menu item is selected."""

    def __init__(
        self, action: Callable | None, display_as: int | str, color: str = "white"
    ):
        """
        :param display_as: Charackter or digit to display in menu, indicating which menu item is selected. Sets :py:attr:`display_as` initially.
        :param color: Color of the status light to indicate which menu item is selected. Sets :py:attr:`color` initially. Defaults to `"white"`.
        :param action: Callback to run on selection.
        """
        super().__init__(display_as, color)
        self.action = action

    def run(self) -> Callable:
        """Getter function for :py:attr:`callback`."""
        self.prepare()
        if self.action:
            self.action()
        self.cleanup()

    def prepare(self):
        """Function to call before :py:attr:`action` is run."""

    def set_action(self, func: Callable | None = None):
        """Setter function for :py:attr:`action`.

        :param func: Function to set as action callback. If not provided, returns a decorator function. Defaults to `None`.
        """

        def decorator(func):
            self.action = func
            return func

        if func:
            return decorator(func)
        return decorator

    def cleanup(self):
        """Function to call after :py:attr:`action` ran."""

    def stop(self):
        """Helper function to stop the callback function of a :py:class:`~gsgr.menu.MenuItem`.

        :raises: :py:class:`~gsgr.exceptions.StopRun`
        """
        raise StopRun


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

    def choose(self) -> MenuItem:
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
                    show_image(
                        self.items[self.position].display_as,
                        self.position == 0,
                        self.position == (len(self.items) - 1),
                        True,
                    )
                    hw.brick.status_light.on(self.items[self.position].color)
                    last_position = self.position

        except (KeyboardInterrupt, SystemExit):
            return self.items[self.position]

    def exit(self):
        """Helper function to exit :py:meth:`~gsgr.menu.Menu.loop`.

        :raises: ExitMenu
        """
        raise ExitMenu


class ActionMenu(Menu):
    items: list[ActionMenuItem]
    """A list of all :py:class:`~gsgr.menu.ActionMenuItem` s in the menu"""

    def choose_and_run(self):
        """Show menu and allow to select item which then is being executed

        :returns: the selected item
        """
        result = self.choose()
        show_image(result.display_as, True, True, False)
        result.prepare()
        try:
            result.action()
        except Exception as e:
            if cnf.debug_mode:
                hw.brick.light_matrix.write(type(e).__name__ + ":" + str(e))
            raise e
        finally:
            result.cleanup()

    def loop(self, autoscroll=False):
        """Show the menu and run the callback of the selected item in an infinite loop.

        :param autoscroll: whether to scroll to the next item after executing the callback of a :py:class:`~gsgr.menu.MenuItem` automatically.
        """
        while True:
            try:
                self.choose_and_run()
            except KeyboardInterrupt:
                continue
            except ExitMenu:
                break

            if autoscroll:
                self.position += 1

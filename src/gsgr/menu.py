"""Module for menu management.

Also supplies run class, being a menu item.
"""

import time
from typing import Callable

import hub

from .configuration import config as cnf
from .configuration import hardware as hw
from .display import show_image
from .exceptions import ExitMenu, StopRun
from .math import clamp


class MenuItem:
    display_as: int | str
    """Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist."""
    color: str
    """Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist."""

    def __init__(self, display_as: int | str, color: str = "white") -> None:
        """
        :param display_as: Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`display_as`.
        :param color: Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`color`. Ist `"white"`, wenn nich angegeben..
        """
        self.display_as = display_as
        self.color = color


class ActionMenuItem(MenuItem):
    action: Callable | None
    """Funktion, die ausgeführt werden soll, falls das Menüelement gewählt wird."""

    def __init__(
        self, action: Callable | None, display_as: int | str, color: str = "white"
    ):
        """
        :param display_as: Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`display_as`.
        :param color: Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`color`. Ist `"white"`, wenn nich angegeben..
        :param action: Callback, der ausgeführt wird, wenn das Menüelement gewählt wird. Setzt :py:attr:`action`.
        """
        super().__init__(display_as, color)
        self.action = action

    def run(self) -> Callable:
        """:py:attr:`callback` unter Berücksichtigung von :py:func:`prepare` und :py:func:`cleanup`."""
        self.prepare()
        if self.action:
            self.action()
        self.cleanup()

    def prepare(self):
        """Wird direkt vor :py:attr:`action` ausgeführt."""

    def set_action(self, func: Callable | None = None):
        """Setter-Funktion für :py:attr:`action`.

        :param func: Funktion, die als Callback festgelegt werden soll. Falls nicht angegeben, wird eine decorator-Funktion zurückgegeben.
        """

        def decorator(func):
            self.action = func
            return func

        if func:
            return decorator(func)
        return decorator

    def cleanup(self):
        """Wird direkt nach :py:attr:`action` ausgeführt."""

    def stop(self):
        """Hilfsfunktion um die Ausführung der Callback-Funktuion vorzeitig zu stoppen.

        :raises: :py:class:`~gsgr.exceptions.StopRun`
        """
        raise StopRun


class Menu:
    """Ein geerellen Menü, welches :py:class:`~gsgr.menu.MenuItem` s enthält"""

    items: list[MenuItem]
    """Eine Liste aller :py:class:`~gsgr.menu.MenuItem` s im Menü"""

    swap_buttons: bool
    """Ob die Funktionen der beiden Buttons getauscht werden sollen"""

    position: int
    """Position des aktuell ausgewählten :py:class:`~gsgr.menu.MenuItem` s"""

    def __init__(self, items: list[MenuItem] | None = None, swap_buttons=False):
        """
        :param items: Eine Liste aller :py:class:`~gsgr.menu.MenuItem` s die bereits im Menü sein sollen. Wenn nicht angegeben, keine.
        :param swap_buttons: Ob die Funktionen der beiden Buttons getauscht werden sollen. Wenn nicht angegeben, :py:`False`.
        """
        self.items = items or []
        self.swap_buttons = swap_buttons
        self.position = 0

    def add_item(self, item: MenuItem):
        """Ein Element zum Menü hinzufügen

        :param item: Hinzuzufügendes Element
        """
        self.items.append(item)

    def choose(self, exit_on_charge=False) -> MenuItem:
        """Menü zeigen und ein Menü-Element wählen lassen.

        :returns: Das gewählte Menü-Element
        """
        last_position = -1
        try:
            while True:
                if hw.brick.left_button.was_pressed():
                    self.position = self.position - (-1 if self.swap_buttons else 1)
                if hw.brick.right_button.was_pressed():
                    self.position = self.position + (-1 if self.swap_buttons else 1)
                if (
                    exit_on_charge
                    and hub.battery.charger_detect()
                    in [
                        hub.battery.CHARGER_STATE_CHARGING_COMPLETED,
                        hub.battery.CHARGER_STATE_CHARGING_ONGOING,
                    ]
                ):
                    if hub.button.connect.is_pressed():
                        exit_on_charge = False
                    else:
                        self.exit()

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

                time.sleep(cnf.loop_throttle)
        except ExitMenu as e:
            raise e
        except (KeyboardInterrupt, SystemExit):
            return self.items[self.position]

    def exit(self):
        """Funktion um :py:meth:`~gsgr.menu.Menu.choose` vorzeitig zu beenden.

        :raises: ExitMenu
        """
        raise ExitMenu


class ActionMenu(Menu):
    items: list[ActionMenuItem]
    """Eine List aller :py:class:`~gsgr.menu.ActionMenuItem` s im Menü"""

    def choose_and_run(self, exit_on_charge=False):
        """Menü zeigen und ein Menü-Element wählen lassen, wessen Callback dann ausgeführt wird

        :returns: Das gewählte Element
        """
        result = self.choose(exit_on_charge=exit_on_charge)
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

    def loop(self, autoscroll=False, exit_on_charge=False):
        """Endlos immer wieder Menü zeigen und ein Menü-Element wählen lassen, welches dann ausgeführt wird.

        :param autoscroll: Ob nach dem erfolgreichen Ausführen eines Callbacks automatisch weitergeblättert werden soll.
        """
        while True:
            try:
                self.choose_and_run(exit_on_charge=exit_on_charge)
            except KeyboardInterrupt:
                continue
            except ExitMenu:
                break

            if autoscroll:
                self.position += 1

"""Module for menu management.

Also supplies run class, being a menu item.
"""

import asyncio

import color
import hub

from .config import cfg
from .display import show_image
from .exceptions import ExitMenu, StopRun
from .math import clamp


class MenuItem:
    display_as: int | str
    """Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist."""
    color: int
    """Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist."""

    def __init__(self, display_as: int | str, color: int = color.WHITE) -> None:
        """
        :param display_as: Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`display_as`.
        :param color: Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`color`. Ist `"white"`, wenn nich angegeben..
        """
        self.display_as = display_as
        self.color = color

    def update(self, first=False) -> bool:
        return False


class ActionMenuItem(MenuItem):
    action: None
    """Funktion, die ausgeführt werden soll, falls das Menüelement gewählt wird."""

    def __init__(
        self,
        action,
        display_as: int | str,
        color_: int = color.WHITE,
    ) -> None:
        """
        :param display_as: Symbol oder Bild, welches von der LED-Matrix angezeigt wird, um anzuzeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`display_as`.
        :param color: Farbe der Statuslampe, um zu zeigen, welches Menüelement ausgewählt ist. Setzt :py:attr:`color`. Ist `"white"`, wenn nich angegeben..
        :param action: Callback, der ausgeführt wird, wenn das Menüelement gewählt wird. Setzt :py:attr:`action`.
        """
        super().__init__(display_as, color_)
        self.action = action

    def run(self) -> None:
        """:py:attr:`callback` unter Berücksichtigung von :py:func:`prepare` und :py:func:`cleanup`."""
        self.prepare()
        if self.action:
            self.action()
        self.cleanup()

    def prepare(self) -> None:
        """Wird direkt vor :py:attr:`action` ausgeführt."""

    def set_action(self, func=None):
        """Setter-Funktion für :py:attr:`action`.

        :param func: Funktion, die als Callback festgelegt werden soll. Falls nicht angegeben, wird eine decorator-Funktion zurückgegeben.
        """

        def decorator(func):
            self.action = func
            return func

        if func:
            return decorator(func)
        return decorator

    def cleanup(self) -> None:
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

    def __init__(self, items: list | None = None, swap_buttons=False, focus: int = 0) -> None:
        """
        :param items: Eine Liste aller :py:class:`~gsgr.menu.MenuItem` s die bereits im Menü sein sollen. Wenn nicht angegeben, keine.
        :param swap_buttons: Ob die Funktionen der beiden Buttons getauscht werden sollen. Wenn nicht angegeben, :py:const:`False`.
        """
        self.items = items or []
        self.swap_buttons = swap_buttons
        self.position = focus

    def add_item(self, item) -> None:
        """Ein Element zum Menü hinzufügen

        :param item: Hinzuzufügendes Element
        """
        self.items.append(item)

    async def choose(self) -> MenuItem:
        """Menü zeigen und ein Menü-Element wählen lassen.

        :returns: Das gewählte Menü-Element
        """
        last_position = -1

        selected = self.items[self.position]

        while not hub.button.pressed(hub.button.POWER):
            if hub.button.pressed(hub.button.LEFT):
                while hub.button.pressed(hub.button.LEFT):
                    ...
                self.position = self.position - (-1 if self.swap_buttons else 1)
            if hub.button.pressed(hub.button.RIGHT):
                while hub.button.pressed(hub.button.RIGHT):
                    ...
                self.position = self.position + (-1 if self.swap_buttons else 1)

            self.position = int(clamp(self.position, 0, len(self.items) - 1))
            selected = self.items[self.position]

            if last_position != self.position:
                show_image(
                    selected.display_as,
                    border_left=self.position == (len(self.items) - 1),
                    border_right=self.position == 0,
                    bright=True,
                )
                hub.light.color(hub.light.POWER, selected.color)
                last_position: int = self.position
                selected.update(first=True)
            selected.update()
            await asyncio.sleep(cfg.LOOP_THROTTLE)
            await asyncio.sleep_ms(10)

        while hub.button.pressed(hub.button.POWER):
            ...
        return selected

    def exit(self):
        """Funktion um :py:meth:`~gsgr.menu.Menu.choose` vorzeitig zu beenden.

        :raises: ExitMenu
        """
        raise ExitMenu


class ActionMenu(Menu):
    items: list[ActionMenuItem]
    """Eine List aller :py:class:`~gsgr.menu.ActionMenuItem` s im Menü"""

    async def choose_and_run(self, exit_on_charge=False) -> None:
        """Menü zeigen und ein Menü-Element wählen lassen, wessen Callback dann ausgeführt wird

        :returns: Das gewählte Element
        """
        # hw.left_color_sensor.light_up_all(0)
        # hw.right_color_sensor.light_up_all(0)

        result: ActionMenuItem = await self.choose()
        show_image(result.display_as, border_right=True, border_left=True, bright=False)
        result.prepare()
        try:
            if not callable(result.action):
                result.cleanup()
                raise RuntimeError("No callback defined!")
            result.action()
        except StopRun as e:
            raise e
        except Exception as e:
            if cfg.DEBUG_DISPLAY_ERRORS:
                hub.light_matrix.write(repr(e))
            raise e
        finally:
            result.cleanup()
        while hub.button.pressed(hub.button.POWER):
            pass

    async def loop(self, autoscroll=False, exit_on_charge=False) -> None:
        """Endlos immer wieder Menü zeigen und ein Menü-Element wählen lassen, welches dann ausgeführt wird.

        :param autoscroll: Ob nach dem erfolgreichen Ausführen eines Callbacks automatisch weitergeblättert werden soll.
        """
        while True:
            try:
                await self.choose_and_run(exit_on_charge=exit_on_charge)
            except StopRun:
                continue
            except ExitMenu:
                break
            if autoscroll:
                self.position += 1

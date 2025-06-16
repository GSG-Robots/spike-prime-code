from typing import Callable, ContextManager

from gsgr.config import cfg
from gsgr.enums import Color
from gsgr.menu import ActionMenuItem


class Run(ActionMenuItem):
    context: ContextManager
    """A context manager in which the run is being executed.

    This is implemented to support :py:class:`~gsgr.config.cfg` changes for individual runs.
    """

    def __init__(
        self,
        display_as: int | str,
        color: Color | int,
        run: Callable,
    ):
        """
        :param display_as: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`display_as` initially.
        :param color: Passed to :py:class:`~gsgr.menu.MenuItem`. Sets :py:attr:`color` initially.
        :param config: A context manager to execute the run in. Designed for :py:class:`~gsgr.config.cfg` calls. Sets :py:attr:`context` initially.
        :param run: The run's main function / callback.
        """
        super().__init__(run, display_as, color)

    def cleanup(self):
        """Patched verison of :py:meth:`MenuItem.cleanup` to stop all motors."""
        cfg.DRIVING_MOTORS.brake()
        cfg.GEAR_SHAFT.float()
        cfg.GEAR_SELECTOR.hold()

from typing import Callable, ContextManager
from gsgr.configuration import config as cnf
from gsgr.movement import free_attachments
from gsgr.menu import ActionMenuItem
from spike import Motor


class Run(ActionMenuItem):
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
        :param run: The run's main function / callback.
        """
        super().__init__(run, display_as, color)
        self.context = config or cnf()

    def prepare(self):
        """Patched verison of :py:meth:`MenuItem.prepare` to enter the context manager / loading run specific config before returning the callback."""
        self.context.__enter__()

    def cleanup(self):
        """Patched verison of :py:meth:`MenuItem.cleanup` to stop all motors and exit the context manager. This means resetting the config."""
        for port in ("A", "B", "C", "D", "E", "F"):
            try:
                Motor(port).stop()
            except RuntimeError:
                ...
        free_attachments()
        self.context.__exit__(None, None, None)

"""Custom exceptions
"""


class WrongUnitError(ValueError):
    """Invalid unit used.

    .. deprecated:: unknown
       We no longer use unit constants.
    """


class BatteryLowError(RuntimeError):
    """Error raised when in debug mode and running motors while battery low.

    Read more :py:func:`here <gsgr.movement.check_battery>`
    """


class EnterDebugMenu(SystemExit):
    """Error raised when debug menu should be started.

    .. deprecated:: unknown
       There is no debug menu anymore."""


class StopRun(KeyboardInterrupt):
    """Raise to stop run immediately.

    Only meant for internal use.
    """


class ExitMenu(SystemExit):
    """Raise to exit menu.

    Only meant for internal use.
    """

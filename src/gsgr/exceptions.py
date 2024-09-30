class WrongUnitError(ValueError):
    """Invalid unit used."""


class BatteryLowError(RuntimeError):
    """Error raised when in debug mode and running motors while battery low."""


class EnterDebugMenu(SystemExit):
    """Error raised when debug menu should be started."""


class StopRun(KeyboardInterrupt):
    """Raise to stop run immediately."""


class ExitMenu(SystemExit):
    """Raise to exit menu"""

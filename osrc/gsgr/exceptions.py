"""Eignene Fehler"""


class BatteryLowError(RuntimeError):
    """Wird geworfen, wenn der Akku zu schwach ist, während sich der Roboter im Debug-Mode befindet.

    Mehr :py:func:`hier <gsgr.movement.check_battery>`
    """


class StopRun(KeyboardInterrupt):
    """Wird geworfen, um einen Run sofort zu stoppen.

    Nur für interne Zwecke gedacht.
    """


class ExitMenu(SystemExit):
    """Wird geworfen, um ein Menü zu verlassen.

    Nur für interne Zwecke gedacht.
    """

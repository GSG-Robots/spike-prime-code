"""Motorsteuerung und Bewegungsfunktionen.
"""

import math
import time
from typing import Generator, Literal, Optional

import hub
from gsgr.config import cfg


# from typing import Iterator
from .conditions import deg
from .exceptions import BatteryLowError, StopRun
from .math import clamp, sigmoid
from .types import Condition
from .enums import Pivot


def check_battery():
    """Helper function to error out on low battery in debug mode.

    This function is ran on all activities including motor movement.
    It will crash the run with the :py:exc:`~gsgr.exceptions.BatteryLowError` if the battery capacity is reported to be below 100%.
    This is meant to force us to keep the robot charged when coding at all times to ensure consistant driving behavior.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError`
    """

    # Only in debug mode
    if not cfg.DEBUG_MODE:
        return
    # Check if the battery is low and raise an error if it is
    if hub.battery.voltage() < 7850:
        raise BatteryLowError


def _wait_until_not_busy(motor):
    while motor.busy(motor.BUSY_MOTOR):
        if hub.button.center.was_pressed():
            raise StopRun


_LAST_SHAFT_SPEED = 0
_GS_STATE = 0
_GS_COMPLETED = True
_GS_SPEED = 100
_GS_TARGET = 0


@cfg.GEAR_SELECTOR.callback
def _gs_callback(state: int):
    global _GS_STATE, _GS_COMPLETED, _GS_SPEED
    _GS_STATE = state
    if state == 0:
        _GS_COMPLETED = True
    elif state == 2:
        _GS_SPEED *= -1
        if cfg.GEAR_SHAFT.busy(cfg.GEAR_SHAFT.BUSY_MOTOR):
            return
        cfg.GEAR_SHAFT.run_for_degrees(
            180, speed=-math.copysign(100, _LAST_SHAFT_SPEED)
        )
        _wait_until_not_busy(cfg.GEAR_SHAFT)
        cfg.GEAR_SELECTOR.run_to_position(
            _GS_TARGET, speed=_GS_SPEED, stop=cfg.GEAR_SELECTOR.STOP_HOLD, stall=True
        )


def _gs_await_completion(timeout: int = 10000):
    start = time.time()
    while not _GS_COMPLETED:
        if timeout and (time.time() - start) > timeout:
            return
        if hub.button.center.was_pressed():
            raise StopRun


def hold_attachment(target_gear: int, await_completion: bool = True):
    """Ausgang wählen um Reibung anzuwenden, gedacht um Anbaute zu halten.
    Select gear to apply torque, meant to hold attachment in place.

    :param target_gear: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]
    :param prepare: Wenn :py:const:`True` angegeben wird, wird der Umschaltprozess nur gestartet, ohne auf Fertigstellung zu warten.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    global _GS_TARGET,_GS_COMPLETED

    check_battery()

    _GS_TARGET = target_gear
    _GS_COMPLETED = False
    cfg.GEAR_SELECTOR.run_to_position(
        target_gear, speed=_GS_SPEED, stop=cfg.GEAR_SELECTOR.STOP_HOLD, stall=True
    )

    if await_completion:
        _gs_await_completion()


def free_attachment(target_gear: int, await_completion: bool = True):
    """Irgeneinen anderen Ausgang auswählen, um Reibung freizugeben, gedacht um Anbaute frei beweglich zu machen.

    Wenn mehrerer Ausgänge zur gleichen Zeit frei beweglich sin sollen, nutze :py:func:`hold_attachment` um einen Ausgang auszuwählen, der nicht freigegeben werden soll.

    Wenn alle Ausgänge zur gleichen Zeit freigegeben werden sollen, nutze :py:func:`free_attachemnts`.

    :param target_gear: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    global _GS_COMPLETED

    check_battery()

    _wait_until_not_busy(cfg.GEAR_SELECTOR)
    target_gear += 90
    if target_gear > 180:
        target_gear -= 360
    _GS_COMPLETED = False
    cfg.GEAR_SELECTOR.run_to_position(target_gear, speed=100)
    if await_completion:
        _gs_await_completion()


def free_attachments():
    """Getriebewähler in eine Stellung bringen, in der in der Theorie Reibung an allen Ausgängen freigegeben wird.

    .. warning::
        Mit Bedacht nutzen, dies kann Ausgänge in manchen Fällen immer noch teilweise blockieren.
        Nur wenn nötig! Nutze :py:func:`free_attachment` wann immer möglich.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    # Move to some position exactly between two gears. moves by 45 degrees.
    # hw.gear_selector.run_to_position(
    #     ((hw.gear_selector.get_position() // 90) * 90 + 45) % 360,
    #     "shortest path",
    #     20,
    # )
    # while cfg.GEAR_SHAFT.busy(cfg.GEAR_SHAFT.BUSY_MOTOR):
    #     ...
    # cfg.GEAR_SHAFT.pwm(0)
    raise NotImplementedError


def run_attachment(
    attachment: int,
    speed: int,
    duration: int | None = None,
    stall: bool = False,
    untension: int | Literal[False] = False,
    await_completion: bool = True,
) -> None:
    """Bewege Ausgang zur angegebenen Zeit oder bis es gestoppt wird

    Wenn mit ``duration`` aufgerufen, wird die Funktion ausgeführt, bis die Zeit um ist. Ansonsten wird der Motor nur gestartet.

    :param attachment: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]
    :param speed: Geschwindigkeit, mit der die Anbaute bewegt werden soll. Wert von -100 bis 100.
    :param duration: Zeit in Sekunden, für die der Ausgang bewegt werden soll. Falls nicht angegeben, wird der Motor nur gestartet.
    :param stop_on_resistance: Ob der Motor vorzeitig stoppen soll, wenn er blockiert wird.
    :param untension: Ob der Motor nach dem Stoppen kurz in die entgegengesetzte Richtung laufen soll, um die Spannung zu lösen.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    global _LAST_SHAFT_SPEED
    check_battery()

    _wait_until_not_busy(cfg.GEAR_SHAFT)

    if _GS_TARGET != attachment:
        hold_attachment(attachment)
    elif not _GS_COMPLETED:
        _gs_await_completion()

    _LAST_SHAFT_SPEED = speed
    if not duration:
        cfg.GEAR_SHAFT.run_at_speed(speed, stall=stall)
    else:
        cfg.GEAR_SHAFT.run_for_time(
            duration * 1000, stop=cfg.GEAR_SHAFT.STOP_BRAKE, speed=speed, stall=stall
        )

    if await_completion:
        _wait_until_not_busy(cfg.GEAR_SHAFT)

    if untension:
        cfg.GEAR_SHAFT.run_for_degrees(
            -math.copysign(untension, speed),
            speed=100,
            stop=cfg.GEAR_SHAFT.STOP_FLOAT,
        )
        _wait_until_not_busy(cfg.GEAR_SHAFT)


def stop_attachment(untension: int | Literal[False] = False, await_completion: bool = False):
    """Ausgangsbewegung stoppen.

    Nur nötig, falls :py:func:`run_attachment` ohne Zieldauer aufgerufen wurde.
    """
    if await_completion:
        _wait_until_not_busy(cfg.GEAR_SHAFT)
    if untension:
        cfg.GEAR_SHAFT.run_for_degrees(
            -math.copysign(untension, _LAST_SHAFT_SPEED),
            speed=100,
            stop=cfg.GEAR_SHAFT.STOP_FLOAT,
        )
        _wait_until_not_busy(cfg.GEAR_SHAFT)


def gyro_set_origin():
    """Gyro-Sensor Origin zurücksetzen"""
    hub.motion.yaw_pitch_roll(0)


def gyro_turn(
    target_angle: int,
    step_speed: int | float = 70,
    pivot: Pivot | int = Pivot.CENTER,
    min_speed: Optional[int] = None,
    max_speed: Optional[int] = None,
    pid: Optional[cfg.PID] = None,
    tolerance: Optional[int] = None,
    timeout: int = 0,
    brake: bool=True
):
    """Drehe mithilfe des Gyrosensors in eine bestimmte Richtung
    
    :param target_angle: Zielgradzahl, auf die gedreht werden soll
    :param step_speed: Drehgeschwindigkeit im Verhältnis zum fehlenden 
                       Drehwinkel; wird multiplikativ angewandt
    :param pivot: Drehpunkt, um den der Roboter dreht; entweder
                  die Mitte des Roboters oder einer seiner Räder
    :param min_speed: Mindestgeschwindigkeit, damit der Roboter beim Drehen nicht stehen bleibt
    :param max_speed: Maximalgeschwindigkeit, damit der Roboter nicht zu langsam entschleunigt
    :param pid: Die PID-Werte für die Bewegung; siehe :py:class:`~gsgr._config.PID`
    :param tolerance: Toleranz beim Auslesen des Gyrosensors
                      (Ziel erreicht wenn Gyro-Wert = Ziel-Wert +- Toleranz)
    :param brake: Ob der Roboter nach der Bewegung bremsen soll
    """

    pid = cfg.GYRO_TURN_PID if pid is None else pid
    min_speed = cfg.GYRO_TURN_MINMAX_SPEED[0] if max_speed is None else max_speed
    max_speed = cfg.GYRO_TURN_MINMAX_SPEED[1] if max_speed is None else max_speed
    tolerance = cfg.GYRO_TOLERANCE if tolerance is None else tolerance

    start_time = time.time()

    if pivot == Pivot.LEFT_WHEEL:
        cfg.LEFT_MOTOR.brake()
    elif pivot == Pivot.RIGHT_WHEEL:
        cfg.RIGHT_MOTOR.brake()

    step_speed /= 100

    speed_last_error = 0
    speed_error_sum = 0

    hub.button.center.was_pressed()
    while True:
        if hub.button.center.was_pressed():
            raise StopRun
        degree_error = target_angle - hub.motion.yaw_pitch_roll()[0]
        target_speed = step_speed * degree_error
        if -min_speed < target_speed < min_speed:
            target_speed = math.copysign(min_speed, target_speed)
        if abs(target_speed) > max_speed:
            target_speed = math.copysign(max_speed, target_speed)
        speed_error = target_speed - hub.motion.gyroscope()[0]
        speed_error_sum += speed_error
        speed_correction = round(
            pid.p * speed_error
            + pid.i * speed_error_sum
            + pid.d * (speed_error - speed_last_error)
        )

        if -tolerance < degree_error < tolerance:
            break
        if timeout and time.time() - start_time > timeout:
            break
        if pivot == Pivot.CENTER:
            cfg.DRIVING_MOTORS.run_at_speed(
                -speed_correction // 2, -speed_correction // 2
            )
        elif pivot == Pivot.LEFT_WHEEL:
            cfg.RIGHT_MOTOR.run_at_speed(-speed_correction)
            # cfg.DRIVING_MOTORS.run_at_speed(0, -speed_correction)
        elif pivot == Pivot.RIGHT_WHEEL:
            # cfg.DRIVING_MOTORS.run_at_speed(-speed_correction, 0)
            cfg.LEFT_MOTOR.run_at_speed(-speed_correction)

        speed_last_error = speed_error
    if brake:
        cfg.DRIVING_MOTORS.brake()


def gyro_drive(
    target_angle: int,
    speed: int | float,
    ending_condition: Generator,
    pid: Optional[cfg.PID] = None,
    accelerate: float = 0,
    decelerate: float = 0,
    sigmoid_conf: tuple[int, bool] = (6, True),
    brake: bool = True,
):
    """Fahre mithilfe des Gyrosensors in eine bestimmte Richtung
    
    :param target_angle: Zielgradzahl; die Richtung in die gefahren werden soll
    :param speed: Fahrgeschwindigkeit; bei negativen Werten fährt der Roboter rückwärts;
                  zwischen -100 und 100
    :param ending_conditon: Zielbedingung;
                            Bis wann/für wie lange die Bewegung ausgeführt werden soll
    :param pid: Die PID-Werte für die Bewegung; siehe :py:class:`~gsgr._config.PID`
    :param accelerate: Über welche Stecke der Roboter beschleunigen soll;
                       in Prozent von der :code:`ending_condition`
    :param decelerate: Über welche Stecke der Roboter entschleunigen soll;
                       in Prozent von der :code:`ending_condition`
    :param brake: Ob der Roboter nach der Bewegung bremsen soll
    """
    smooth, stretch = sigmoid_conf
    cutoff = sigmoid(-smooth) if stretch else 0

    pid = cfg.GYRO_DRIVE_PID if pid is None else pid
    last_error = 0
    error_sum = 0

    hub.button.center.was_pressed()
    while (pct := next(ending_condition)) < 100:
        if hub.button.center.was_pressed():
            raise StopRun
        error = target_angle - hub.motion.yaw_pitch_roll()[0]
        error_sum += error
        correction = round(
            pid.p * error + pid.i * error_sum + pid.d * (error - last_error)
        )

        left_speed, right_speed = speed + correction // 2, speed - correction // 2

        if pct < accelerate:
            speed_mutiplier = clamp(
                round(
                    (sigmoid((pct / accelerate * 2 * smooth) - smooth) - cutoff)
                    / (1 - cutoff),
                    2,
                ),
                0.2,
                1,
            )
            left_speed, right_speed = (
                left_speed * speed_mutiplier,
                right_speed * speed_mutiplier,
            )
        if 100 - pct < decelerate:
            speed_mutiplier = clamp(
                round(
                    (
                        sigmoid(((decelerate - pct) / decelerate * 2 * smooth) - smooth)
                        - cutoff
                    )
                    / (1 - cutoff),
                    2,
                ),
                0.2,
                1,
            )
            left_speed, right_speed = (
                left_speed * speed_mutiplier,
                right_speed * speed_mutiplier,
            )

        if -5 < left_speed < 5:
            left_speed = math.copysign(5, left_speed)

        if -5 < right_speed < 5:
            right_speed = math.copysign(5, right_speed)

        cfg.DRIVING_MOTORS.run_at_speed(-left_speed, right_speed)

        last_error = error
    if brake:
        cfg.DRIVING_MOTORS.brake()

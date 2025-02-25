"""Motorsteuerung und Bewegungsfunktionen.
"""

import math
import time
from typing import Literal

import hub
from gsgr.config import cfg

from . import correctors as corr

# from typing import Iterator
from .conditions import deg
from .exceptions import BatteryLowError, StopRun
from .math import clamp, sigmoid
from .types import Condition
from .utils import Timer


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
    :param prepare: Wenn :py:const:`True` angegeben wird, wird der umschaltprozess nur gestartet, ohne auf fertigstellung zu warten.

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


def stop_attachment(untension: int | Literal[False] = False, await_completion: bool = True):
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


def drive(speed_generator: Condition, until_generator: Condition):
    """Generelle Fahrfunktion. Nutzt die gegebenen Generatoren für Geschwindigkeit und Ziel. Hauptsächlich für interne Nutzung.

    :param speed_generator: Ein Generator, der die Geschwindigkeit angibt, mit der gefahren werden soll. [TODO: Read more]
    :param until_generator: Ein Generator, der angibt, wann die Bewegung beendet werden soll. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    last_left, last_right = 0, 0
    pair = hub.port.F.motor.pair(hub.port.E.motor)
    while next(until_generator) < 100:
        if hub.button.center.was_pressed():
            raise StopRun

        left_speed, right_speed = next(speed_generator)

        if 0 < left_speed < 5:
            left_speed = 5
        if 0 < right_speed < 5:
            right_speed = 5
        if -5 < left_speed < 0:
            left_speed = -5
        if -5 < right_speed < 0:
            right_speed = -5

        left_speed = clamp(-100, left_speed, 100)
        right_speed = clamp(-100, right_speed, 100)

        if (
            left_speed,
            right_speed,
        ) != (
            last_left,
            last_right,
        ):
            pair.run_at_speed(-left_speed, right_speed)

        last_left, last_right = left_speed, right_speed

        time.sleep(cfg.LOOP_THROTTLE)
    # hw.driving_motors.stop()
    pair.hold()


def gyro_drive(
    degree: int,
    speed: int,
    do_for: Condition,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    gyro_tolerance: int | None = None,
    # accelerate_from: Condition | None = None,
    accelerate_for: Condition | None = None,
    decelerate_from: Condition | None = None,
    decelerate_for: Condition | None = None,
):
    """Gyro Drive

    :param degree: Richtung in die Gefahren bzw. Korrigiert werden soll. Wert von -180 bis 180
    :param speed: Geschwindigkeit, mit der gefahren werden soll. Wert von 0 bis 100.
    :param do_for: Zielbedingung [TODO: Read more]
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: Toleranz für Zielgradzahl. Nutzt globale Konfiguration, falls nicht angegeben.
    :param accelerate_for: Bedingung, die angibt, bis wann Beschleunigt werden soll.
    :param decelerate_from: Bedingung, die angibt, ab wann Entschleunigt werden soll.
    :param decelerate_for: Bedingung, die angibt, wie lange Entschleunigt werden soll.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    corrector = corr.speed(speed)

    # Auto-setup acceleration and deceleration
    if accelerate_for:
        corrector = corr.accelerate_sigmoid(
            corrector,
            accelerate_for,
            # accelerate_from,
            smooth=2,
        )

    if decelerate_for:
        corrector = corr.decelerate(
            corrector,
            decelerate_from,
            decelerate_for,
        )

    # Auto-setup PID
    corrector = corr.gyro_drive_pid(
        corrector,
        degree,
        p_correction,
        i_correction,
        d_correction,
        gyro_tolerance,
    )

    # Delegate to normal drive function
    drive(
        corrector,
        do_for,
    )


def gyro_turn(
    degree: int,
    speed: int = 80,
    do_for: Condition | None = None,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    gyro_tolerance: int | None = None,
    accelerate_for: Condition | None = None,
    decelerate_from: Condition | None = None,
    decelerate_for: Condition | None = None,
):
    """Gyro Turn

    :param degree: Richtung in die Gedreht bzw. Korrigiert werden soll. Wert von -180 bis 180
    :param speed: Geschwindigkeit, mit der gedreht werden soll. Wert von 0 bis 100.
    :param do_for: Zielbedingung [TODO: Read more]
    :param p_correction: p correction value. Defaults to general config.
    :param i_correction: i correction value. Defaults to general config.
    :param d_correction: d correction value. Defaults to general config.
    :param gyro_tolerance: Toleranz für Zielgradzahl. Nutzt globale Konfiguration, falls nicht angegeben.
    :param accelerate_for: Bedingung, die angibt, bis wann Beschleunigt werden soll.
    :param decelerate_from: Bedingung, die angibt, ab wann Entschleunigt werden soll.
    :param decelerate_for: Bedingung, die angibt, wie lange Entschleunigt werden soll.
    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    corrector = corr.speed(speed)

    # Auto-setup acceleration and deceleration
    if accelerate_for:
        corrector = corr.accelerate_sigmoid(
            corrector,
            accelerate_for,
            # accelerate_from,
            smooth=2,
        )

    if decelerate_for and decelerate_from:
        corrector = corr.decelerate(
            corrector,
            decelerate_from,
            decelerate_for,
        )

    # Auto-setup PID
    corrector = corr.gyro_turn_pid(
        corrector,
        degree,
        p_correction,
        i_correction,
        d_correction,
        gyro_tolerance,
    )

    # Delegate to normal drive function
    drive(
        corrector,
        do_for or deg(degree),
    )


def gyro_set_origin(set_to=0):
    """Gyro-Sensor Origin zurücksetzen"""
    hub.motion.yaw_pitch_roll(0)


class Pivot:
    # LEFT_WHEEL_REVERSE = -2
    LEFT_WHEEL = -1
    CENTER = 0
    RIGHT_WHEEL = 1
    # RIGHT_WHEEL_REVERSE = 2


def gyro_speed_turn(
    target_angle: int,
    step_speed: int | float = 70,
    pivot: Pivot | int = Pivot.CENTER,
    min_speed: int | None = None,
    max_speed: int | None = None,
    pid: cfg.PID | None = None,
    tolerance: int | None = None,
):

    pid = cfg.GYRO_DRIVE_PID if pid is None else pid
    min_speed = cfg.GYRO_SPEED_TURN_MINMAX_SPEED[0] if max_speed is None else max_speed
    max_speed = cfg.GYRO_SPEED_TURN_MINMAX_SPEED[1] if max_speed is None else max_speed
    tolerance = cfg.GYRO_TOLERANCE if tolerance is None else tolerance

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
            cfg.DRIVING_MOTORS.brake()
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


def gyro_drive2(
    target_angle: int,
    speed: int | float,
    ending_condition,
    pid: cfg.PID | None = None,
    accelerate: float = 0,
    decelerate: float = 0,
    sigmoid_conf: tuple[int, bool] = (6, True),
    brake: bool = True,
):
    smooth, stretch = sigmoid_conf
    cutoff = sigmoid(-smooth) if stretch else 0

    pid = cfg.GYRO_DRIVE2_PID if pid is None else pid
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

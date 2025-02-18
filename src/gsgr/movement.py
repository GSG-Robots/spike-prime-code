"""Motorsteuerung und Bewegungsfunktionen.
"""

import math
import time

import hub
from gsgr.config import cfg

from . import correctors as corr

# from typing import Iterator
from .conditions import deg
from .exceptions import BatteryLowError, StopRun
from .math import clamp
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
    if hub.battery.voltage() < 8000:
        raise BatteryLowError


def hold_attachment(target_gear: int):
    """Ausgang wählen um Reibung anzuwenden, gedacht um Anbaute zu halten.
    Select gear to apply torque, meant to hold attachment in place.

    :param target_gear: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    check_battery()
    # Move to the target gear position Gear 1 is at 0 degrees, Gear 2 is at 90 degrees, etc.
    cfg.GEAR_SELECTOR.run_to_position(
        90 * (target_gear - 1), speed=100, stop=hub.STOP_HOLD
    )


def free_attachment(target_gear: int):
    """Irgeneinen anderen Ausgang auswählen, um Reibung freizugeben, gedacht um Anbaute frei beweglich zu machen.

    Wenn mehrerer Ausgänge zur gleichen Zeit frei beweglich sin sollen, nutze :py:func:`hold_attachment` um einen Ausgang auszuwählen, der nicht freigegeben werden soll.

    Wenn alle Ausgänge zur gleichen Zeit freigegeben werden sollen, nutze :py:func:`free_attachemnts`.

    :param target_gear: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    check_battery()
    # Move to some other position. Anything over 45 degrees will do, but 90 is the most reliable.
    cfg.GEAR_SHAFT.float()
    cfg.GEAR_SELECTOR.run_to_position(((90 * (target_gear - 1)) + 90) % 360, speed=100)


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
    cfg.GEAR_SHAFT.float()


def run_attachment(
    attachment: int,
    speed: int,
    duration: int | None = None,
    stop_on_resistance: bool = False,
    untension: bool = False,
) -> None:
    """Bewege Ausgang zur angegebenen Zeit oder bis es gestoppt wird

    Wenn mit ``duration`` aufgerufen, wird die Funktion ausgeführt, bis die Zeit um ist. Ansonsten wird der Motor nur gestartet.

    :param attachment: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]
    :param speed:Geschwindigkeit, mit der die Anbaute bewegt werden soll. Wert von -100 bis 100.
    :param duration: Zeit in Sekunden, für die der Ausgang bewegt werden soll. Falls nicht angegeben, wird der Motor nur gestartet.
    :param stop_on_resistance: Ob der Motor vorzeitig stoppen soll, wenn er blockiert wird.
    :param untension: Ob der Motor nach dem Stoppen kurz in die entgegengesetzte Richtung laufen soll, um die Spannung zu lösen.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    # Stop the drive shaft if it is running
    cfg.GEAR_SHAFT.brake()
    # Select the target gear, this is the same as holding the attachment
    hold_attachment(attachment)
    # Move at the specified speed for the specified duration or until resistance is detected (if stop_on_resistance is True)
    # hw.drive_shaft.set_stall_detection(stop_on_resistance)
    cfg.GEAR_SHAFT.run_at_speed(speed)
    if not duration:
        return
    if stop_on_resistance:
        timer = Timer()
        while (
            timer.elapsed
            < duration
            # and not hw.drive_shaft.was_stalled()
            # and not hw.drive_shaft.was_interrupted()
        ):
            time.sleep(cfg.LOOP_THROTTLE)
            if hub.button.center.was_pressed():
                raise StopRun
    else:
        timer = Timer()
        while timer.elapsed < duration:
            time.sleep(cfg.LOOP_THROTTLE)
            if hub.button.center.was_pressed():
                raise StopRun
    cfg.GEAR_SHAFT.brake()
    # Cleanup
    if untension:
        cfg.GEAR_SHAFT.run_for_degrees(
            -math.copysign(80, speed)
        )  # -80 * (speed // abs(speed))


def stop_attachment():
    """Ausgangsbewegung stoppen.

    Nur nötig, falls :py:func:`run_attachment` ohne Zieldauer aufgerufen wurde.
    """
    # check_battery()
    # Stop the drive shaft
    cfg.GEAR_SHAFT.float()


def drive(speed_generator: Condition, until_generator: Condition, use_power=True):
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

        left_speed = -clamp(-100, left_speed, 100)
        right_speed = clamp(-100, right_speed, 100)

        if (
            left_speed,
            right_speed,
        ) != (
            last_left,
            last_right,
        ):
            pair.run_at_speed(left_speed, right_speed)
            # TODO
            # if use_power:

            #     hw.driving_motors.start_tank_at_power(

            #         round(left_speed),  #  / 100 * 70 + math.copysign(30, left_speed)

            #         round(right_speed),  #  / 100 * 70 + math.copysign(30, right_speed)

            #     )

            # else:

            #     hw.driving_motors.start_tank(

            #         round(left_speed),

            #         round(right_speed),

            #     )

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
        use_power=False,
    )


def gyro_set_origin(set_to=0):
    """Gyro-Sensor Origin zurücksetzen"""
    hub.motion.yaw_pitch_roll(0)

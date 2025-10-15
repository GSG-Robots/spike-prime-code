"""Motorsteuerung und Bewegungsfunktionen."""

import math
import time

import hub
import motor
import motor_pair

from . import buttons
from .config import PID, cfg
from .enums import Pivot, SWSensor

# from typing import Iterator
from .exceptions import BatteryLowError, StopRun
from .interpolators import exponential, linear
from .math import clamp
from .types import Condition


def check_battery():
    """Helper function to error out on low battery in debug mode.

    This function is ran on all activities including motor movement.
    It will crash the run with the :py:exc:`~gsgr.exceptions.BatteryLowError` if the battery capacity is reported to be below 100%.
    This is meant to force us to keep the robot charged when coding at all times to ensure consistant driving behavior.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError`
    """

    # Only in debug mode
    if not cfg.DEBUG_RAISE_BATTERY:
        return
    # Check if the battery is low and raise an error if it is
    if hub.battery_voltage() < 7850:
        raise BatteryLowError


def _wait_until_not_busy(m):
    while motor.status(m) == motor.RUNNING:
        if buttons.pressed(hub.button.POWER):
            raise StopRun


_LAST_SHAFT_SPEED = 0


def _gs_await_completion(timeout: int = 5):
    if motor.status(cfg.GEAR_SELECTOR) != motor.RUNNING:
        return
    start = time.time()
    sign = 1
    time.sleep(0.1)
    while motor.status(cfg.GEAR_SELECTOR) == motor.RUNNING:
        if timeout and (time.time() - start) > timeout:
            return
        motor.run_for_degrees(cfg.GEAR_SHAFT, sign * 10, 500)
        time.sleep(0.1)
        sign = -sign
        if buttons.pressed(hub.button.POWER):
            raise StopRun


def hold_attachment(target_gear: int, await_completion: bool = True):
    """Ausgang wählen um Reibung anzuwenden, gedacht um Anbaute zu halten.
    Select gear to apply torque, meant to hold attachment in place.

    :param target_gear: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]
    :param prepare: Wenn :py:const:`True` angegeben wird, wird der Umschaltprozess nur gestartet, ohne auf Fertigstellung zu warten.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    check_battery()

    motor.run_to_absolute_position(
        cfg.GEAR_SELECTOR,
        target_gear + cfg.GEAR_SELECTOR_OFFSET,
        1000,
        direction=motor.SHORTEST_PATH,
        stop=motor.HOLD,
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
    hold_attachment(target_gear + 90, await_completion)


def free_attachments(await_completion: bool = True):
    """Getriebewähler in eine Stellung bringen, in der in der Theorie Reibung an allen Ausgängen freigegeben wird.

    .. warning::
        Mit Bedacht nutzen, dies kann Ausgänge in manchen Fällen immer noch teilweise blockieren.
        Nur wenn nötig! Nutze :py:func:`free_attachment` wann immer möglich.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    hold_attachment(motor.absolute_position(cfg.GEAR_SELECTOR) // 90 * 90 + 45, await_completion)


def run_attachment(attachment: int, speed: int, duration: int | float | None = None, stall: bool = False, untension: int | None = None, await_completion: bool = True, when_i_say_duration_i_mean_degrees: bool = False) -> None:
    """Bewege Ausgang zur angegebenen Zeit oder bis es gestoppt wird

    Wenn mit ``duration`` aufgerufen, wird die Funktion ausgeführt, bis die Zeit um ist. Ansonsten wird der Motor nur gestartet.

    :param attachment: Die Nummer des Ausgangs. Nutze am besten :py:class:`gsgr.enums.Attachment`. [TODO: Read more]
    :param speed: Geschwindigkeit, mit der die Anbaute bewegt werden soll. Wert von -100 bis 100.
    :param duration: Zeit in Sekunden, für die der Ausgang bewegt werden soll. Falls nicht angegeben, wird der Motor nur gestartet.
    :param stop_on_resistance: Ob der Motor vorzeitig stoppen soll, wenn er blockiert wird.
    :param untension: Wie viel Grad der Motor nach dem Stoppen kurz in die entgegengesetzte Richtung laufen soll, um die Spannung zu lösen.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    global _LAST_SHAFT_SPEED
    check_battery()

    _wait_until_not_busy(cfg.GEAR_SHAFT)

    hold_attachment(attachment)
    _gs_await_completion()

    _LAST_SHAFT_SPEED = speed
    if not duration:
        motor.run(cfg.GEAR_SHAFT, speed)
    else:
        # cfg.GEAR_SHAFT.pwm(speed)
        # time.sleep(duration)
        # cfg.GEAR_SHAFT.brake()
        if when_i_say_duration_i_mean_degrees:
            motor.run_for_degrees(cfg.GEAR_SHAFT, int(duration), speed, stop=motor.HOLD)
        else:
            motor.run_for_time(cfg.GEAR_SHAFT, int(duration * 1000), speed, stop=motor.HOLD)
        # cfg.GEAR_SHAFT.run_for_time(
        #     duration * 1000, stop=cfg.GEAR_SHAFT.STOP_BRAKE, speed=speed, stall=stall
        # )

    if await_completion:
        _wait_until_not_busy(cfg.GEAR_SHAFT)

    if untension:
        motor.run_for_degrees(cfg.GEAR_SHAFT, -int(math.copysign(untension, _LAST_SHAFT_SPEED)), 1000)
        _wait_until_not_busy(cfg.GEAR_SHAFT)


def stop_attachment(untension: int = False, await_completion: bool = False):
    """Ausgangsbewegung stoppen.

    Nur nötig, falls :py:func:`run_attachment` ohne Zieldauer aufgerufen wurde.
    """
    if await_completion:
        _wait_until_not_busy(cfg.GEAR_SHAFT)
    motor.stop(cfg.GEAR_SHAFT, stop=motor.HOLD)
    if untension:
        motor.run_for_degrees(cfg.GEAR_SHAFT, -math.copysign(untension, _LAST_SHAFT_SPEED), 1000)
        _wait_until_not_busy(cfg.GEAR_SHAFT)


def gyro_set_origin():
    """Gyro-Sensor Origin zurücksetzen"""
    hub.motion_sensor.reset_yaw(0)


def gyro_wall_align(wall_align_duration: int | float = 1, backwards: bool = False):
    speed = -300 if backwards else 300
    motor_pair.move_tank(cfg.DRIVING_MOTORS, -speed, -speed)
    time.sleep(wall_align_duration / 2)
    hub.motion_sensor.reset_yaw(0)
    time.sleep(wall_align_duration / 2)
    motor_pair.stop(cfg.DRIVING_MOTORS, stop=motor.COAST)


def gyro_turn(
    target_angle: int,
    step_speed: int | float = 120,
    pivot: Pivot | int = Pivot.CENTER,
    min_speed: int | None = None,
    max_speed: int | None = None,
    pid: PID | None = None,
    tolerance: int | None = None,
    timeout: int = 0,
    brake: bool = True,
    premature_ending_condition=None,
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

    target_angle = target_angle + cfg.GYRO_OFF / 360 * target_angle

    pid = cfg.GYRO_TURN_PID if pid is None else pid
    min_speed = cfg.GYRO_TURN_MINMAX_SPEED[0] if max_speed is None else max_speed
    max_speed = cfg.GYRO_TURN_MINMAX_SPEED[1] if max_speed is None else max_speed
    tolerance = cfg.GYRO_TOLERANCE if tolerance is None else tolerance

    start_time = time.time()

    if pivot == Pivot.LEFT_WHEEL:
        motor.stop(cfg.LEFT_MOTOR, stop=motor.BRAKE)
    elif pivot == Pivot.RIGHT_WHEEL:
        motor.stop(cfg.RIGHT_MOTOR, stop=motor.BRAKE)

    step_speed /= 100

    speed_last_error = 0
    speed_error_sum = 0

    buttons.pressed(hub.button.POWER)
    while (premature_ending_condition is None) or (next(premature_ending_condition) != 100):
        if buttons.pressed(hub.button.POWER):
            raise StopRun
        degree_error = target_angle - hub.motion_sensor.tilt_angles()[0] // 10
        target_speed = step_speed * degree_error
        if -min_speed < target_speed < min_speed:
            target_speed = math.copysign(min_speed, target_speed)
        if abs(target_speed) > max_speed:
            target_speed = math.copysign(max_speed, target_speed)
        speed_error = target_speed * 10 - hub.motion_sensor.angular_velocity()[0]
        speed_error_sum += speed_error
        speed_correction = round(pid.p * speed_error + pid.i * speed_error_sum + pid.d * (speed_error - speed_last_error))

        if -tolerance < degree_error < tolerance:
            break
        if timeout and time.time() - start_time > timeout:
            break
        if pivot == Pivot.CENTER:
            motor_pair.move_tank(motor_pair.PAIR_1, -int(speed_correction / 2), int(speed_correction / 2))
        elif pivot == Pivot.LEFT_WHEEL:
            motor.run(cfg.RIGHT_MOTOR, int(speed_correction / 1.5))
        elif pivot == Pivot.RIGHT_WHEEL:
            motor.run(cfg.LEFT_MOTOR, int(speed_correction / 1.5))

        speed_last_error = speed_error
    if brake:
        motor_pair.stop(cfg.DRIVING_MOTORS, stop=motor.HOLD)


def sign(n):
    if n < 0:
        return -1
    else:
        return 1


def gyro_drive(
    target_angle: int,
    speed: int | float,
    ending_condition: Condition,
    pid: PID | None = None,
    accelerate: float = 0,
    decelerate: float = 0,
    interpolators=(exponential, linear),
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
    target_angle = target_angle + cfg.GYRO_OFF / 360 * target_angle

    pid = cfg.GYRO_DRIVE_PID if pid is None else pid
    last_error = 0
    error_sum = 0
    last = time.ticks_us()

    while (pct := next(ending_condition)) < 100:
        if hub.button.pressed(hub.button.POWER):
            while hub.button.pressed(hub.button.POWER):
                ...
            raise StopRun
        error = target_angle * 10 - hub.motion_sensor.tilt_angles()[0]
        # if abs(error) < cfg.GYRO_TOLERANCE:
        #     # error = 0
        #     error_sum = 0
        #     last_error = 0
        now = time.ticks_us()
        error_sum += error * (time.ticks_diff(now, last) / 1000000)
        last = now
        correction = clamp(
            round(pid.p * error + pid.i * error_sum + pid.d * (error - last_error)),
            -1500,
            1500,
        )

        if sign(error) != sign(error_sum):
            error_sum = 0
            # last_error = 0

        left_speed, right_speed = speed - correction // 2, speed + correction // 2
        if pct < accelerate:
            speed_multiplier = interpolators[0](0.2, 1, pct / accelerate)
            left_speed, right_speed = (
                left_speed * speed_multiplier,
                right_speed * speed_multiplier,
            )
        if (100 - pct) < decelerate:
            speed_multiplier = interpolators[1](0.2, 1, (100 - pct) / decelerate)
            left_speed, right_speed = (
                left_speed * speed_multiplier,
                right_speed * speed_multiplier,
            )

        motor_pair.move_tank(cfg.DRIVING_MOTORS, int(left_speed), int(right_speed))

        last_error = error
        # time.sleep(cfg.LOOP_THROTTLE)
    if brake == 69.42:
        motor_pair.stop(cfg.DRIVING_MOTORS, stop=motor.COAST)
    elif brake:
        motor_pair.stop(cfg.DRIVING_MOTORS, stop=motor.HOLD)


def start_with_naR(alpha, radius):
    assert cfg.LEFT_SW_SENSOR == SWSensor.INTEGRATED_LIGHT, "naR: left sensor must be the integrated light sensor"
    assert cfg.RIGHT_SW_SENSOR == SWSensor.INTEGRATED_LIGHT, "naR: right sensor must be the integrated light sensor"

    cfg.LEFT_SENSOR.mode(4)
    cfg.RIGHT_SENSOR.mode(4)
    time.sleep(0.1)

    ...

"""Motor control functions and presets
"""

import time
from typing import Iterator
from .conditions import deg
from . import correctors as corr
from .math import clamp
import hub

from .types import Condition

# from .conditions import Deg, Sec
from .configuration import config
from .configuration import hardware as hw

# from .correctors import (
# AccelerateSec,
# Corrector,
# DecelerateSec,
# GyroDrivePID,
# GyroTurnPID,
# )
from .exceptions import BatteryLowError
from .utils import Timer


def check_battery():
    """Helper function to error out on low battery in debug mode.

    This function is ran on all activities including motor movement.
    It will crash the run with the :py:exc:`~gsgr.exceptions.BatteryLowError` if the battery capacity is reported to be below 100%.
    This is meant to force us to keep the robot charged when coding at all times to ensure consistant driving behavior.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError`
    """

    # Only in debug mode
    if not config.debug_mode:
        return
    # Check if the battery is low and raise an error if it is
    if hub.battery.capacity_left() < 100:
        raise BatteryLowError("Battery capacity got below 100%")


def hold_attachment(target_gear: int):
    """Select gear to apply torque, meant to hold attachment in place.

    :param target_gear: The number of the attachment gear. Preferably use the :py:class:`gsgr.enums.Attachment` enum. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    check_battery()
    # Move to the target gear position Gear 1 is at 0 degrees, Gear 2 is at 90 degrees, etc.
    hw.gear_selector.run_to_position(90 * (target_gear - 1), "shortest path", 100)


def free_attachment(target_gear: int):
    """Select any other gear to release torque, meant to enable the attachment of moving freely.

    When multiple attachments need to be freed at the same time, use :py:func:`hold_attachment` to specifically select one attachment not to be freed.

    When all attachments need to be freed at the same time, use :py:func:`free_attachemnts`.

    :param target_gear: The number of the attachment gear. Preferably use the :py:class:`gsgr.enums.Attachment` enum. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    check_battery()
    # Move to some other position. Anything over 45 degrees will do, but 90 is the most reliable.
    hw.gear_selector.run_to_position(
        ((90 * (target_gear - 1)) + 90) % 360, "shortest path", 100
    )


def free_attachments():
    """Move gearshaft into a position between two attachments to release torque on all attachments at the same time, meant to enable all attachments of moving freely.

    .. warning::
        Use with care, this may still parially lock attachments in place from time to time.
        Only use if really needed! Check :py:func:`free_attachment` whenever possible.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    # Move to some position exactly between two gears. moves by 45 degrees.
    hw.gear_selector.run_to_position(
        ((hw.gear_selector.get_position() // 90) * 90 + 45) % 360,
        "shortest path",
        20,
    )


def run_attachment(
    attachment: int,
    speed: int,
    duration: int | None = None,
    stop_on_resistance: bool = False,
    untension: bool = False,
) -> None:
    """Move attachment for given time or until stopped

    If run with ``duration``, runs until duration passed. If run without ``duration``, only starts and call finished immideately after starting motor.

    :param attachment: The number of the attachment gear. Preferably use the :py:class:`gsgr.enums.Attachment` enum. [TODO: Read more]
    :param speed: Speed to move attachment at, in percent. Value from 0 to 100.
    :param duration: Time in seconds to stop after. If not supplied, motor will be started without ending condition.
    :param stop_on_resistance: Whether to stop the motion if the motor reports it is being blocked/stalled.
    :param untension: Whether to shortly unselect the attachment gear after the motion. This can be used to release tension and stress on parts after moving against a blockade.

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    # Stop the drive shaft if it is running
    hw.drive_shaft.stop()
    # Select the target gear, this is the same as holding the attachment
    hold_attachment(attachment)
    # Move at the specified speed for the specified duration or until resistance is detected (if stop_on_resistance is True)
    hw.drive_shaft.set_stall_detection(stop_on_resistance)
    hw.drive_shaft.start(speed)
    if not duration:
        return
    if stop_on_resistance:
        timer = Timer()
        while timer.elapsed < duration and not hw.drive_shaft.was_stalled() and not hw.drive_shaft.was_interrupted():
            time.sleep(config.loop_throttle)
    else:
        time.sleep(duration)
    hw.drive_shaft.stop()
    # Cleanup
    if untension:
        hw.drive_shaft.run_for_degrees(-80 * (speed // abs(speed)))


# def run_attachment_degrees(
#     attachment: int,
#     speed: int,
#     degrees: int = None,
#     stop_on_resistance: bool = False,
# ):
#     check_battery()
#     # Stop the drive shaft if it is running
#     hw.drive_shaft.stop()
#     start = hw.drive_shaft.get_position()
#     # Select the target gear, this is the same as holding the attachment
#     hold_attachment(attachment)
#     # Move at the specified speed for the specified duration or until resistance is detected (if stop_on_resistance is True)
#     if stop_on_resistance:
#         hw.drive_shaft.set_stall_detection(True)
#     hw.drive_shaft.start(speed)
#     if not degrees:
#         return
#     while abs(hw.drive_shaft.get_position() - start) < degrees:
#         if stop_on_resistance and hw.drive_shaft.was_stalled():
#             break
#     hw.drive_shaft.stop()
#     # Cleanup
#     hw.drive_shaft.set_stall_detection(False)


def stop_attachment():
    """Stop attachment movement. Only needed if :py:func:`run_attachment` was called without duration."""
    # check_battery()
    # Stop the drive shaft
    hw.drive_shaft.stop()


def drive(
    speed_generator: Condition,
    until_generator: Condition,
):
    """General drive function, mostly only for internal use.

    :param speed_generator: a generator supplying speeds at request. [TODO: Read more]
    :param until_generator: a generator reporting whether the motion is finished. [TODO: Read more]

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """
    check_battery()
    last_left, last_right = 0, 0
    while next(until_generator) < 100:
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
            hw.driving_motors.start_tank(
                round(left_speed * config.speed_multiplier),
                round(right_speed * config.speed_multiplier),
            )

        last_left, last_right = left_speed, right_speed

        time.sleep(config.loop_throttle)
    hw.driving_motors.stop()


def gyro_drive(
    degree: int,
    speed: int,
    do_for: Condition,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    gyro_tolerance: int | None = None,
    accelerate_from: Condition | None = None,
    accelerate_for: Condition | None = None,
    decelerate_from: Condition | None = None,
    decelerate_for: Condition | None = None,
):
    """Gyro Drive. Shortcut for :py:func:`drive` with :py:func:`~gsgr.correctors.gyro_drive_pid` as speed generator.

    :param degree: Direction to drive in/correct towards. Value from -180 to 180
    :param speed: Speed to drive at, in percent. Value from 0 to 100.
    :param do_for: Condition to end at. [TODO: Read more]
    :param p_correction: P Correction Value for PID-Controller. Defaults to general config.
    :param i_correction: I Correction Value for PID-Controller. Defaults to general config.
    :param d_correction: D Correction Value for PID-Controller. Defaults to general config.
    :param gyro_tolerance: D Correction Value for PID-Controller. Defaults to general config.
    :param accelerate_from: Condition to start accelerating at. (Don't know why anyone would ever want to do this...) Same values as for :py:obj:`do_for`
    :param accelerate_for: Condition to determine how long to accelerate. Same values as for :py:obj:`do_for`
    :param decelerate_from: Condition to start deccelerating at. Same values as for :py:obj:`do_for`
    :param decelerate_for: Condition to determine how long to deccelerate. Same values as for :py:obj:`do_for`

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    corrector = corr.speed(speed)

    # Auto-setup acceleration and deceleration
    if accelerate_for:
        corrector = corr.accelerate(
            corrector,
            accelerate_for,
            accelerate_from,
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
    accelerate_from: Condition | None = None,
    accelerate_for: Condition | None = None,
    decelerate_from: Condition | None = None,
    decelerate_for: Condition | None = None,
):
    """Gyro Drive. Shortcut for :py:func:`drive` with :py:func:`~gsgr.correctors.gyro_drive_pid` as speed generator.

    :param degree: Direction to turn towards. Value from -180 to 180
    :param speed: Speed to turn at, in percent. Value from 0 to 100.
    :param do_for: Condition to end at. Use none to end when target direction is reached. [TODO: Read more]
    :param p_correction: P Correction Value for PID-Controller. Defaults to general config.
    :param i_correction: I Correction Value for PID-Controller. Defaults to general config.
    :param d_correction: D Correction Value for PID-Controller. Defaults to general config.
    :param gyro_tolerance: D Correction Value for PID-Controller. Defaults to general config.
    :param accelerate_from: Condition to start accelerating at. (Don't know why anyone would ever want to do this...) Same values as for :py:obj:`do_for`
    :param accelerate_for: Condition to determine how long to accelerate. Same values as for :py:obj:`do_for`
    :param decelerate_from: Condition to start deccelerating at. Same values as for :py:obj:`do_for`
    :param decelerate_for: Condition to determine how long to deccelerate. Same values as for :py:obj:`do_for`

    :raises: :py:exc:`~gsgr.exceptions.BatteryLowError` (more: :py:func:`check_battery`)
    """

    corrector = corr.speed(speed)

    # Auto-setup acceleration and deceleration
    if accelerate_for:
        corrector = corr.accelerate(
            corrector,
            accelerate_for,
            accelerate_from,
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
    """Reset Gyro-Sensor Origin. Should be used at least once in the beginnign of each run."""
    config.degree_o_meter.reset(set_to)

import time
from .conditions import deg
from . import correctors as corr
from .math import clamp
import hub

from ._condition_base import ConditionBase

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
    # Only in debug mode
    if not config.debug_mode:
        return
    # Check if the battery is low and raise an error if it is
    # if hub.battery.capacity_left() < 80:
    #     raise BatteryLowError("Battery capacity got below 80%")


def hold_attachment(target_gear: int):
    check_battery()
    # Move to the target gear position Gear 1 is at 0 degrees, Gear 2 is at 90 degrees, etc.
    hw.gear_selector.run_to_position(90 * (target_gear - 1), "shortest path", 100)


def free_attachment(target_gear: int):
    check_battery()
    # Move to some other position. Anything over 45 degrees will do, but 90 is the most reliable.
    hw.gear_selector.run_to_position(
        (90 * (target_gear - 1)) + 90, "shortest path", 100
    )


def free_attachments():
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

    :param attachment: Number of attachment to move, value of enum :py:class:`gsgr.enums.Attachment`
    :param speed: Speed to move attachment at, in percent. Value from 0-100
    :param duration: Time in seconds to stop after. If not supplied motor will be started without ending condition.
    """
    check_battery()
    # Stop the drive shaft if it is running
    hw.drive_shaft.stop()
    # Select the target gear, this is the same as holding the attachment
    hold_attachment(attachment)
    # Move at the specified speed for the specified duration or until resistance is detected (if stop_on_resistance is True)
    timer = Timer()
    if stop_on_resistance:
        hw.drive_shaft.set_stall_detection(True)
    hw.drive_shaft.start(speed)
    if not duration:
        return
    while timer.elapsed < duration:
        if stop_on_resistance and hw.drive_shaft.was_stalled():
            break
    hw.drive_shaft.stop()
    # Cleanup
    hw.drive_shaft.set_stall_detection(False)
    if untension:
        free_attachment(attachment)
        hold_attachment(attachment)

def run_attachment_degrees(
    attachment: int,
    speed: int,
    degrees: int = None,
    stop_on_resistance: bool = False,
):
    check_battery()
    # Stop the drive shaft if it is running
    hw.drive_shaft.stop()
    start = hw.drive_shaft.get_position()
    # Select the target gear, this is the same as holding the attachment
    hold_attachment(attachment)
    # Move at the specified speed for the specified duration or until resistance is detected (if stop_on_resistance is True)
    if stop_on_resistance:
        hw.drive_shaft.set_stall_detection(True)
    hw.drive_shaft.start(speed)
    if not degrees:
        return
    while abs(hw.drive_shaft.get_position() - start) < degrees:
        if stop_on_resistance and hw.drive_shaft.was_stalled():
            break
    hw.drive_shaft.stop()
    # Cleanup
    hw.drive_shaft.set_stall_detection(False)


def stop_attachment():
    # check_battery()
    # Stop the drive shaft
    hw.drive_shaft.stop()


def drive(
    speed_generator,
    until_generator,
):
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
    do_for: ConditionBase,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    gyro_tolerance: int | None = None,
    accelerate_from = None,
    accelerate_for = None,
    decelerate_from = None,
    decelerate_for = None,
):
    # Auto-setup PID
    corrector = corr.gyro_drive_pid(
        corr.speed(speed),
        degree,
        p_correction,
        i_correction,
        d_correction,
        gyro_tolerance,
    )

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

    # Delegate to normal drive function
    drive(
        corrector,
        do_for,
    )


def gyro_turn(
    degree: int,
    speed: int = 80,
    do_for: ConditionBase | None = None,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    gyro_tolerance: int | None = None,
    accelerate_from = None,
    accelerate_for = None,
    decelerate_from = None,
    decelerate_for = None,
):
    # Auto-setup PID
    corrector = corr.gyro_drive_pid(
        corr.speed(speed),
        degree,
        p_correction,
        i_correction,
        d_correction,
        gyro_tolerance,
    )

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

    # Delegate to normal drive function
    drive(
        corrector,
        do_for or deg(degree),
    )


def gyro_set_origin(set_to=0):
    config.degree_o_meter.reset(set_to)

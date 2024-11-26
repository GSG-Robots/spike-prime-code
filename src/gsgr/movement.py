import time
from gsgr.conditions import deg
import gsgr.correctors as corr
from gsgr.math import clamp
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
    if hub.battery.capacity_left() < 100:
        raise BatteryLowError("Battery capacity got below 100%")


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
    duration: int = None,
    stop_on_resistance: bool = False,
):
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
    while not next(until_generator):
        left_speed, right_speed = next(speed_generator)

        if 0 < left_speed < 5:
            left_speed = 5
        if 0 < right_speed < 5:
            right_speed = 5
        if -5 < left_speed < 0:
            left_speed = -5
        if -5 < right_speed < 0:
            right_speed = -5

        left_speed = clamp(-100, left_speed // 5 * 5, 100)
        right_speed = clamp(-100, right_speed // 5 * 5, 100)

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
    accelerate_for: int = 0,
    decelerate_for: int = 0,
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
    if accelerate_for > 0:
        if do_for[0] == 2:
            corrector = corr.accelerate_sec(
                corrector,
                accelerate_for,
                0,
            )

    if decelerate_for > 0:
        # if isinstance(do_for, Sec):
        if do_for[0] == 2:
            corrector = corr.decelerate_sec(
                corrector,
                decelerate_for,
                do_for[1] - decelerate_for,
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
    accelerate_for: int = 0,
    decelerate_for: int = 0,
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
    if accelerate_for > 0:
        corrector = corr.accelerate_sec(
            corrector,
            accelerate_for,
            0,
        )
    if decelerate_for > 0:
        corrector = corr.accelerate_sec(
            corrector,
            9999,
            decelerate_for,
        )

    # Delegate to normal drive function
    drive(
        corrector,
        do_for or deg(degree),
    )


def gyro_set_origin(set_to=0):
    config.degree_o_meter.reset(set_to)

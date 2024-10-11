from .conditions import Sec, Deg
from .correctors import (
    AccelerateSec,
    Corrector,
    DecelerateSec,
    GyroDrivePID,
    GyroTurnPID,
)
from ._condition_base import ConditionBase
from .exceptions import BatteryLowError
import hub
from .utils import Timer
from .configuration import config, hardware as hw


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
    hw.gear_selector.run_to_position((90 * (target_gear - 1)) + 90, "shortest path", 100)


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
    duration: int,
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
    while timer.elapsed < duration:
        if stop_on_resistance and hw.drive_shaft.was_stalled():
            break
    hw.drive_shaft.stop()
    # Cleanup
    hw.drive_shaft.set_stall_detection(False)


def stop_attachment():
    check_battery()
    # Stop the drive shaft
    hw.drive_shaft.stop()


def drive(
    speed: int,
    until: ConditionBase,
    correctors: list[Corrector] | Corrector = None,
):
    if correctors is None:
        correctors = []
    correctors = [correctors] if not isinstance(correctors, list) else correctors
    check_battery()
    until.setup()
    for corrector in correctors:
        corrector.setup()
    while not until.check():
        left_speed = speed
        right_speed = speed
        for corrector in correctors:
            left_speed, right_speed = corrector.apply(left_speed, right_speed)

        if 0 < left_speed < 5:
            left_speed = 5
        if 0 < right_speed < 5:
            right_speed = 5
        if -5 < left_speed < 0:
            left_speed = -5
        if -5 < right_speed < 0:
            right_speed = -5

        # print(left_speed, right_speed)

        hw.driving_motors.start_tank(
            round(left_speed * config.speed_multiplier),
            round(right_speed * config.speed_multiplier),
        )
    hw.driving_motors.stop()


def gyro_drive(
    speed: int,
    degree: int,
    do_for: ConditionBase,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    accelerate_for: int = 0,
    decelerate_for: int = 0,
):
    # Auto-setup PID
    correctors = [GyroDrivePID(degree, p_correction, i_correction, d_correction)]

    # Auto-setup acceleration and deceleration
    if accelerate_for > 0:
        if isinstance(do_for, Sec):
            correctors.append(
                AccelerateSec(
                    accelerate_for,
                    0,
                )
            )
    if decelerate_for > 0:
        if isinstance(do_for, Sec):
            correctors.append(
                DecelerateSec(
                    decelerate_for,
                    do_for.value - decelerate_for,
                )
            )

    # Delegate to normal drive function
    drive(
        speed,
        do_for,
        correctors,
    )


def gyro_turn(
    degree: int,
    speed: int = 80,
    do_for: ConditionBase | None = None,
    p_correction: int | None = None,
    i_correction: int | None = None,
    d_correction: int | None = None,
    accelerate_for: int = 0,
    decelerate_for: int = 0,
):
    # Auto-setup PID
    correctors = [GyroTurnPID(degree, p_correction, i_correction, d_correction)]

    # Auto-setup acceleration and deceleration
    if accelerate_for > 0:
        if isinstance(do_for, Sec):
            correctors.append(
                AccelerateSec(
                    accelerate_for,
                    0,
                )
            )
    if decelerate_for > 0:
        if isinstance(do_for, Sec):
            correctors.append(
                DecelerateSec(
                    decelerate_for,
                    do_for.value - decelerate_for,
                )
            )

    # Delegate to normal drive function
    drive(
        speed,
        do_for or Deg(degree),
        correctors,
    )


def gyro_set_origin(set_to=0):
    config.degree_o_meter.reset(set_to)

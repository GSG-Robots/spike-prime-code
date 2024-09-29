from gsgr import config, hardware
from gsgr.conditions import Sec
from gsgr.correctors import AccelerateSec, DecelerateSec, GyroDrivePID
from gsgr.movement import gyro_drive, drive
from spike import Motor, MotorPair, PrimeHub


def main():
    # drive(
    #     80,
    #     Sec(10),
    #     [
    #         GyroDrivePID(0),
    #         AccelerateSec(duration=5),
    #         DecelerateSec(duration=5, delay=5),
    #     ],
    # )
    gyro_drive(80, 0, Sec(10), accelerate_for=5, decelerate_for=5)

with (
    hardware(
        drive_shaft=Motor("B"),
        gear_selector=Motor("A"),
        driving_motors=MotorPair("E", "F"),
        left_motor=Motor("E"),
        right_motor=Motor("F"),
        brick=PrimeHub(),
        tire_radius=2.6,
    ),
    config(
        p_correction=1.5,
        i_correction=0,
        d_correction=-0.2,
        speed_multiplier=1,
        debug_mode=False,
        error_threshold=1,
    ),
):
    main()

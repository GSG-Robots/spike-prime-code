from gsgr import config, hardware
from gsgr.conditions import Cm, Sec
from gsgr.correctors import Acceleration, Deceleration, GyroDrivePID
from gsgr.run import Run
from spike import Motor, MotorPair, PrimeHub


def main():
    run = Run()
    run.drive(
        80,
        Sec(10),
        [
            GyroDrivePID(0),
            Acceleration(duration=5),
            Deceleration(duration=5, delay=5),
        ],
    )


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
        debug_mode=True,
        error_threshold=1,
    ),
):
    main()

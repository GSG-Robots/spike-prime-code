from gsgr import config, hardware
from gsgr.conditions import Sec
from gsgr.correctors import AccelerationSecCorrecor
from gsgr.run import Run
from spike import Motor, MotorPair, PrimeHub


def main():
    run = Run()
    run.drive(80, Sec(6), AccelerationSecCorrecor(5))


with (
    hardware(
        drive_shaft=Motor("A"),
        gear_selector=Motor("B"),
        driving_motors=MotorPair("E", "F"),
        left_motor=Motor("E"),
        right_motor=Motor("F"),
        brick=PrimeHub(),
        tire_radius=2.6,
    ),
    config(p_correction=1.5, i_correction=0, d_correction=-0.2, speed_multiplier=1),
):
    main()

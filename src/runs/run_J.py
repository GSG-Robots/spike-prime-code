import color as col

from ..gsgr.movement import gyro_set_origin, run_attachment

display_as = "J"
color = col.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()

    run_attachment(-90, 1000, 1)
    run_attachment(0, 1000, 1)
    run_attachment(90, 1000, 1)
    run_attachment(180, 1000, 1)

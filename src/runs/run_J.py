from ..gsgr.enums import Color
from ..gsgr.movement import (
    gyro_set_origin,
    run_attachment,
)

display_as = "J"
color = Color.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()

    run_attachment(-90, 100, 1)
    run_attachment(0, 100, 1)
    run_attachment(90, 100, 1)
    run_attachment(180, 100, 1)

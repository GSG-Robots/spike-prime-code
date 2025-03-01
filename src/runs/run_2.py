import time
from gsgr.conditions import cm, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
    Pivot
)

display_as = 2
color = Color.WHITE


# FEATURE FLAGS
# x Sekunden
FEATURE_KORALLEN = True
# #############


# Gesamt: x Sekunden
def run():

    # Anbaute homen
    # if FEATURE_KORALLEN:
        # run_attachment(Attachment.FRONT_RIGHT, 100, 1.3, untension=False)
        # run_attachment(Attachment.FRONT_RIGHT, -100, 1, False, True)
    run_attachment(
        Attachment.FRONT_LEFT, 75, 1, stall=True, untension=0
    )
    # hold_attachment(Attachment.FRONT_LEFT, False)
    
    # Set Gyro Origin
    gyro_drive(0, -50, sec(1))
    gyro_set_origin()
    # hold_attachment(Attachment.FRONT_LEFT, True)

    # Fahre zu Schiff
    gyro_drive(0, 65, cm(12))
    gyro_turn(45, 110, Pivot.RIGHT_WHEEL, min_speed=4)
    gyro_drive(45, 65, cm(17.5))
    gyro_turn(0, 90, Pivot.LEFT_WHEEL, min_speed=2)
    gyro_drive(0, 65, cm(11))

    # Sachen einsammeln
    run_attachment(Attachment.FRONT_LEFT, -95, 1.5, True, untension=90)
    hold_attachment(Attachment.BACK_RIGHT, await_completion=False)
    gyro_drive(0, 20, cm(5.5))

    # Mast stellen
    run_attachment(
        Attachment.BACK_RIGHT, 100, 3.7, stall=True
    )

    if FEATURE_KORALLEN:
        run_attachment(
            Attachment.BACK_RIGHT, -75, 1.8
        )
        run_attachment(Attachment.FRONT_RIGHT, -100, 2, stall=True)

        # gyro_turn(-10, 120, Pivot.LEFT_WHEEL, min_speed=2)
        gyro_drive(0, 70, cm(11))
        time.sleep(0.75)
        gyro_drive(0, -70, cm(7))

    gyro_drive(45, -100, sec(3))
    gyro_turn(-45, 150, Pivot.LEFT_WHEEL)

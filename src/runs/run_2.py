import time

from gsgr.conditions import OR, THEN, cm, deg, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    free_attachment,
    gyro_drive2,
    gyro_set_origin,
    gyro_speed_turn,
    hold_attachment,
    run_attachment,
    Pivot
)

display_as = 2
color = Color.WHITE


# FEATURE FLAGS
# 14 Sekunden
FEATURE_KORALLEN = False
# #############


# Gesamt: 26 Sekunden
def run():

    # Anbaute homen
    if FEATURE_KORALLEN:
        run_attachment(Attachment.FRONT_RIGHT, 100, 1.3, untension=False)
        run_attachment(Attachment.FRONT_RIGHT, -100, 1, False, True)
    run_attachment(
        Attachment.FRONT_LEFT, 75, 1, stop_on_resistance=True, untension=0
    )
    
    # Set Gyro Origin
    gyro_drive2(0, -30, sec(.5))
    gyro_set_origin()

    # Fahre zu Schiff
    gyro_drive2(0, 65, cm(12), brake=True)
    gyro_speed_turn(45, 110, Pivot.RIGHT_WHEEL, min_speed=4)
    gyro_drive2(45, 65, cm(20))#, decelerate_from=cm(15), decelerate_for=cm(7))
    gyro_speed_turn(0, 90, Pivot.LEFT_WHEEL, min_speed=2)
    gyro_drive2(0, 65, cm(7))#, decelerate_from=cm(15), decelerate_for=cm(7))

    # Sachen einsammeln
    run_attachment(Attachment.FRONT_LEFT, -95, 1.5, True, untension=90)
    hold_attachment(Attachment.BACK_RIGHT)
    gyro_drive2(0, 20, cm(5.5))

    # Mast stellen
    run_attachment(
        Attachment.BACK_RIGHT, 100, 3.7, stop_on_resistance=True, untension=0
    )

    if FEATURE_KORALLEN:
        run_attachment(Attachment.BACK_RIGHT, -100, 1.5, untension=True)

        # Fahre zu Korallen
        gyro_drive2(0, 70, cm(6))

        # Korallenbank
        run_attachment(Attachment.FRONT_RIGHT, 100, 1.8, stop_on_resistance=True)
        run_attachment(Attachment.FRONT_RIGHT, -100, 1.2, True, True)

        gyro_drive2(0, -50, cm(3))

    gyro_drive2(45, -100, sec(3))

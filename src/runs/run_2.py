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
    # Set Gyro Origin
    gyro_set_origin()

    # Anbaute homen
    if FEATURE_KORALLEN:
        run_attachment(Attachment.FRONT_RIGHT, 100, 1.3, untension=False)
        run_attachment(Attachment.FRONT_RIGHT, -100, 1, False, True)
    run_attachment(
        Attachment.FRONT_LEFT, 75, 1, stop_on_resistance=True, untension=True
    )

    # Fahre zu Schiff
    gyro_drive2(0, -30, sec(.25))
    gyro_set_origin()
    gyro_drive2(0, 75, cm(10))
    gyro_speed_turn(45, 120, Pivot.RIGHT_WHEEL, min_speed=4)
    gyro_drive2(45, 75, cm(20))#, decelerate_from=cm(15), decelerate_for=cm(7))
    gyro_speed_turn(0, 100, Pivot.LEFT_WHEEL, min_speed=2)
    hold_attachment(Attachment.BACK_RIGHT)
    gyro_drive2(0, 75, cm(9))#, decelerate_from=cm(15), decelerate_for=cm(7))

    # Mast stellen
    run_attachment(
        Attachment.BACK_RIGHT, 100, 3.7, stop_on_resistance=True, untension=True
    )

    if FEATURE_KORALLEN:
        run_attachment(Attachment.BACK_RIGHT, -100, 1.5, untension=True)

        # Fahre zu Korallen
        gyro_drive2(0, 70, cm(6))

        # Korallenbank
        run_attachment(Attachment.FRONT_RIGHT, 100, 1.8, stop_on_resistance=True)
        run_attachment(Attachment.FRONT_RIGHT, -100, 1.2, True, True)

        gyro_drive2(0, -50, cm(3))

    # Sachen einsammeln
    hold_attachment(Attachment.FRONT_LEFT)
    gyro_drive2(0, 90, cm(4))
    run_attachment(Attachment.FRONT_LEFT, -95, 1, True, False)

    # Zurück zu base
    # gyro_drive(0, -75, cm(5))
    # gyro_turn(35, 50, OR(deg(35), sec(2)))
    # gyro_drive(45, -100, cm(70))
    gyro_drive2(45, -100, sec(3))

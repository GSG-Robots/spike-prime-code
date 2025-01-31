import time
from gsgr.conditions import sec, deg, cm, OR
from gsgr.enums import Color, Attachment
from gsgr.movement import (
    gyro_set_origin,
    gyro_drive,
    gyro_turn,
    run_attachment,
    hold_attachment,
    free_attachment,
)

display_as = 2
color = Color.WHITE


def run():
    # Set Gyro Origin
    gyro_set_origin()
    
    # Anbaute homen
    run_attachment(Attachment.FRONT_RIGHT, 100, 1.3, untension=False)
    run_attachment(Attachment.FRONT_RIGHT, -100, 1, False, True)
    run_attachment(Attachment.FRONT_LEFT, 75, 1, stop_on_resistance=True, untension=True)

    # Fahre zu Schiff
    gyro_drive(0, 90, cm(11))
    gyro_turn(45, 50)
    gyro_drive(45, 75, cm(20))
    gyro_turn(0, 50)
    gyro_drive(0, 75, cm(21))

    # Mast stellen
    run_attachment(Attachment.BACK_RIGHT, 100, 3.5, stop_on_resistance=True)
    run_attachment(Attachment.BACK_RIGHT, -100, 1.5, untension=True)

    # Fahre zu Korallen
    gyro_drive(0, 70, cm(6))

    # Korallenbank
    run_attachment(Attachment.FRONT_RIGHT, 100, 1.8, stop_on_resistance=True)
    run_attachment(Attachment.FRONT_RIGHT, -100, 1.2, True, True)
    
    # Sachen einsammeln
    run_attachment(Attachment.FRONT_LEFT, -80, 1.5, True, False)

    # Zurück zu base
    gyro_drive(0, -75, cm(5))
    gyro_turn(35, 50, OR(deg(35), sec(2))) 
    gyro_drive(45, -100, cm(70))

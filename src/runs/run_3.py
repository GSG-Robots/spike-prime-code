import time

from gsgr.conditions import THEN, cm, deg, sec
from gsgr.correctors import speed
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    drive,
    free_attachment,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
)

display_as = 3
color = Color.BLUE

# FEATURE FLAGS
# 6 Sekunden
FEATURE_TOWER = True
# #############


# Gesamt: 16 Sekunden
def run():
    # Set Gyro Origin
    gyro_set_origin()
    run_attachment(Attachment.FRONT_LEFT, -20, 1)

    # Zum Boot fahren
    gyro_drive(0, 40, cm(20), accelerate_for=cm(10))
    # Boot nach vorne schieben
    gyro_drive(0, 70, cm(75), accelerate_for=cm(10))

    # Plankton yeeten
    run_attachment(Attachment.FRONT_RIGHT, 100, 1, True, True)

    if FEATURE_TOWER:
        run_attachment(Attachment.FRONT_LEFT, 50, 0.2)
        # Turm aufstellen
        for i in range(7):
            run_attachment(Attachment.FRONT_LEFT, 50, 0.25)
            gyro_drive(0, -20 - i * 1.5, cm(1))

            time.sleep(0.05 * i)

    # In die andere Base fahren
    gyro_drive(0, -90, cm(15))

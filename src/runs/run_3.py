import time
from gsgr.conditions import cm
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    stop_attachment,
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
    gyro_drive(0, 30, cm(20), accelerate=50, brake=False)
    # Boot nach vorne schieben
    gyro_drive(0, 70, cm(75), accelerate=12)

    # Plankton yeeten
    run_attachment(Attachment.BACK_RIGHT, -100, 2, stall=True, untension=90)

    gyro_drive(0, -25, cm(1.5))

    if FEATURE_TOWER:
        # Turm aufstellen
        run_attachment(Attachment.FRONT_LEFT, 100, stall=False, await_completion=False)
        gyro_drive(0, -8, cm(7))
        time.sleep(1)
        stop_attachment(await_completion=False)

    # In die andere Base fahren
    gyro_drive(0, -90, cm(15))

from gsgr.conditions import THEN, cm, deg, sec

from gsgr.enums import Attachment, Color

from gsgr.movement import (
    free_attachment,

    gyro_drive,

    gyro_set_origin,

    gyro_turn,

    hold_attachment,
    run_attachment,
)


display_as = 4

color = Color.RED



def run():

    # Set Gyro Origin

    gyro_set_origin()


    gyro_drive(0, -80, cm(5))


    # Plankton yeeten
    run_attachment(

        Attachment.BACK_LEFT, -85, 1, stall=True, untension=True
    )


    # Arm homen

    run_attachment(Attachment.BACK_LEFT, 50, 1, stall=True, untension=True)


    # Zu Quadropus fahren

    gyro_drive(1, -70, cm(38), decelerate_for=cm(12), decelerate_from=cm(30))


    # Sachen sammeln

    run_attachment(Attachment.BACK_LEFT, -30, 1.5)


    # Zurück zu base

    gyro_drive(0, 50, cm(60), p_correction=0.3)

    free_attachment(Attachment.BACK_LEFT)


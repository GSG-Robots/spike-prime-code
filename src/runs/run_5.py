from gsgr.conditions import THEN, cm, impact, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    Pivot,
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    hold_attachment,
    run_attachment,
    stop_attachment,
)

display_as = 5
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_drive(0, -30, sec(0.5))
    gyro_set_origin()

    # zum Wal fahren
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(0, 80, cm(66), accelerate=5, decelerate=5)
    gyro_turn(45, 95, Pivot.RIGHT_WHEEL)
    gyro_drive(45, 70, impact(cm(13)), accelerate=5, decelerate=10)
    run_attachment(Attachment.FRONT_RIGHT, -50, 2, untension=180)
    gyro_set_origin()

    # vom Wal wegfahren
    gyro_drive(0, -70, cm(11.5))
    gyro_turn(45, 110, Pivot.LEFT_WHEEL)

    # zum Sonar fahren
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_drive(45, -60, cm(33.5), accelerate=10, decelerate=10)
    run_attachment(Attachment.FRONT_LEFT, 70, 3, stall=True)
    gyro_drive(45, -70, cm(9), accelerate=10, brake=False)
    run_attachment(Attachment.FRONT_LEFT, -100, 2.5, await_completion=False, stall=True)
    gyro_drive(45, -70, cm(20), decelerate=10)
    gyro_turn(135, 90, pivot=Pivot.LEFT_WHEEL)
    gyro_turn(170, 130, pivot=Pivot.RIGHT_WHEEL, timeout=2.5)
    gyro_turn(135, 130, pivot=Pivot.RIGHT_WHEEL, min_speed=10)
    stop_attachment(untension=180, await_completion=True)
    hold_attachment(Attachment.BACK_LEFT, await_completion=False)
    gyro_drive(135, -50, THEN(cm(11), sec(1)), decelerate=20)
    run_attachment(Attachment.BACK_LEFT, 100, 3, stall=True)
    hold_attachment(Attachment.BACK_RIGHT, await_completion=False)
    gyro_drive(135, 50, cm(10), decelerate=10)
    gyro_turn(90, 110, pivot=Pivot.LEFT_WHEEL)
    gyro_drive(90, 40, cm(15))
    run_attachment(Attachment.BACK_RIGHT, 100, 1, stall=True)

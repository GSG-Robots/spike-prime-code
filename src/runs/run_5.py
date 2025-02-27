from gsgr.conditions import cm, sec
from gsgr.enums import Attachment, Color
from gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    run_attachment,
    hold_attachment,
    stop_attachment,
    Pivot,
)

display_as = 5
color = Color.RED


def run():
    # Set Gyro Origin
    gyro_set_origin()

    #zum Wal fahren
    hold_attachment(Attachment.FRONT_RIGHT, await_completion=False)
    gyro_drive(0, 70, cm(68), accelerate=3, decelerate=3)
    gyro_turn(45, 95, Pivot.RIGHT_WHEEL)
    gyro_drive(45, 70, cm(15), decelerate=20)
    run_attachment(Attachment.FRONT_RIGHT, -50, 2, await_completion=False)
    gyro_drive(45, 30, sec(1))
    stop_attachment(untension=180)
    hold_attachment(Attachment.FRONT_LEFT, await_completion=False)
    gyro_set_origin()

    #vom Wal wegfahren
    gyro_drive(0, -70, cm(6.5))
    gyro_turn(45, 110, Pivot.LEFT_WHEEL)

    #zum Sonar fahren
    gyro_drive(45, -60, cm(37), accelerate=10, decelerate=10)
    run_attachment(Attachment.FRONT_LEFT, 70, 3, stall=True)
    gyro_drive(45, -70, cm(9), accelerate=10, brake=False)
    run_attachment(Attachment.FRONT_LEFT, -100, 2.5, await_completion=False, stall=True)
    gyro_drive(45, -70, cm(20), decelerate=10)
    gyro_turn(135, 90, pivot=Pivot.LEFT_WHEEL)
    gyro_turn(160, 130, pivot=Pivot.RIGHT_WHEEL, timeout=3)
    gyro_turn(135, 130, pivot=Pivot.RIGHT_WHEEL)
    stop_attachment(untension=180, await_completion=True)
    hold_attachment(Attachment.BACK_LEFT, await_completion=False)
    gyro_drive(135, -50, cm(13), decelerate=20)
    run_attachment(Attachment.BACK_LEFT, -100, 2.5, stall=True)
    hold_attachment(Attachment.BACK_RIGHT, await_completion=False)
    gyro_drive(135, 50, cm(10), decelerate=10)
    gyro_turn(90, 110, pivot=Pivot.LEFT_WHEEL)
    gyro_drive(90, 40, cm(15))
    run_attachment(Attachment.BACK_RIGHT, 100, 1, stall=True)

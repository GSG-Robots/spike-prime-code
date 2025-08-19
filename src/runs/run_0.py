from ..gsgr.config import PID
from ..gsgr.conditions import cm
from ..gsgr.enums import Attachment, Color
from ..gsgr.movement import gyro_drive, gyro_wall_align, run_attachment

display_as = 0
color = Color.PINK


def run():
    run_attachment(Attachment.BACK_LEFT, 100, 0.5)
    run_attachment(Attachment.BACK_LEFT, -100, 0.5)
    run_attachment(Attachment.BACK_LEFT, 100, 0.5)
    run_attachment(Attachment.BACK_LEFT, -100, 0.5)
    run_attachment(Attachment.BACK_LEFT, 100, 0.5)
    run_attachment(Attachment.BACK_LEFT, -100, 0.5)
    run_attachment(Attachment.BACK_LEFT, 100, 0.5)

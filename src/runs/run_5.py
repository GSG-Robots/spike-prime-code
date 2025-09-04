import time

import color as col

from ..gsgr.conditions import cm, impact, pickup
from ..gsgr.config import cfg
from ..gsgr.enums import Attachment, Pivot
from ..gsgr.movement import (
    gyro_drive,
    gyro_set_origin,
    gyro_turn,
    gyro_wall_align,
    hold_attachment,
    run_attachment,
)

display_as = 5
color = col.RED

def run(): ...

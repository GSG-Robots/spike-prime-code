import gc
import os
import time

import color as col
import hub
import orientation

from .gsgr import buttons, movement
from .gsgr.config import cfg
from .gsgr.enums import Attachment
from .gsgr.menu import ActionMenu, ActionMenuItem
from .gsgr.run import Run

TEN = [
    100,
    0,
    100,
    100,
    100,
    100,
    0,
    100,
    0,
    100,
    100,
    0,
    100,
    0,
    100,
    100,
    0,
    100,
    0,
    100,
    100,
    0,
    100,
    100,
    100,
]

RIGHT_ARROW = [
    0,
    100,
    0,
    0,
    0,
    0,
    100,
    100,
    0,
    0,
    0,
    100,
    100,
    100,
    0,
    0,
    100,
    100,
    0,
    0,
    0,
    100,
    0,
    0,
    0,
]
LEFT_ARROW = [
    0,
    0,
    0,
    100,
    0,
    0,
    0,
    100,
    100,
    0,
    0,
    100,
    100,
    100,
    0,
    0,
    0,
    100,
    100,
    0,
    0,
    0,
    0,
    100,
    0,
]


def run_motorcontrol():
    """Motorcontrol"""
    select = 1
    last_select = -1
    motor = Attachment.FRONT_LEFT
    while not buttons.pressed(hub.button.POWER):
        if hub.button.pressed(hub.button.LEFT):
            select -= 1
            time.sleep(0.2)
            while hub.button.pressed(hub.button.LEFT):
                time.sleep(0.2)
                select -= 1
        if hub.button.pressed(hub.button.RIGHT):
            select += 1
            time.sleep(0.2)
            while hub.button.pressed(hub.button.RIGHT):
                time.sleep(0.2)
                select += 1
        if select < 1:
            select = 4
        if select > 4:
            select = 1
        if last_select != select:
            last_select = select
            hub.light_matrix.clear()
            if select == 1:
                hub.light_matrix.set_pixel(0, 0, 100)
                motor = Attachment.FRONT_LEFT
            if select == 2:
                hub.light_matrix.set_pixel(4, 0, 100)
                motor = Attachment.FRONT_RIGHT
            if select == 3:
                hub.light_matrix.set_pixel(0, 4, 100)
                motor = Attachment.BACK_LEFT
            if select == 4:
                hub.light_matrix.set_pixel(4, 4, 100)
                motor = Attachment.BACK_RIGHT
            movement.hold_attachment(motor, False)
    direction_speed = 1
    speed = 10
    is_inverted = motor in (Attachment.FRONT_RIGHT, Attachment.BACK_RIGHT)
    hub.light_matrix.clear()
    hub.light_matrix.show(RIGHT_ARROW if is_inverted else LEFT_ARROW)
    while not buttons.pressed(hub.button.POWER):
        if buttons.pressed(hub.button.RIGHT):
            direction_speed = 1
            hub.light_matrix.show(RIGHT_ARROW if is_inverted else LEFT_ARROW)
        if buttons.pressed(hub.button.LEFT):
            direction_speed = -1
            hub.light_matrix.show(LEFT_ARROW if is_inverted else RIGHT_ARROW)
    hub.light_matrix.show(TEN)
    while not buttons.pressed(hub.button.POWER):
        if buttons.pressed(hub.button.RIGHT):
            speed = min(speed + 1, 10)
            if speed == 10:
                hub.light_matrix.show(TEN)
            else:
                hub.light_matrix.write(str(speed))
        if buttons.pressed(hub.button.LEFT):
            speed = max(speed - 1, 0)
            hub.light_matrix.write(str(speed))
    speed = direction_speed * 100 * speed
    movement.run_attachment(motor, speed)
    while not buttons.pressed(hub.button.POWER):
        time.sleep(0.1)
    movement.stop_attachment()
    time.sleep(1.0)


async def main():
    gc.collect()
    mem_perc = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc()) * 100
    print(f"{mem_perc}% of memory used")
    print("Voltage:", hub.battery_voltage(), "mV")
    # Align display depending on config
    if cfg.LANDSCAPE:
        hub.light_matrix.set_orientation(orientation.RIGHT)
    else:
        hub.light_matrix.set_orientation(orientation.UP)

    # Initialize Menu
    menu = ActionMenu(swap_buttons=cfg.LANDSCAPE, focus=cfg.DEBUG_FOCUS)

    # Load runs from runs/*.py
    for file in sorted(os.listdir("/flash/src/runs"), key=str.lower):
        run = getattr(__import__("src.runs.%s" % file[:-4]).runs, file[:-4])
        display_as = run.display_as
        color = run.color
        run_action = run.run
        left_sensor = run.left_sensor if hasattr(run, "left_sensor") else None
        right_sensor = run.right_sensor if hasattr(run, "right_sensor") else None
        assert isinstance(display_as, (int, str)), "RunDef: display_as must be str or int"
        assert isinstance(color, int), "RunDef: color must be int"
        assert left_sensor is None or (
            isinstance(left_sensor, tuple)
            and len(left_sensor) == 2
            and isinstance(left_sensor[0], int)
            and isinstance(left_sensor[1], int)
        ), "RunDef: left_sensor must be None or tuple of two ints"
        assert right_sensor is None or (
            isinstance(right_sensor, tuple)
            and len(right_sensor) == 2
            and isinstance(right_sensor[0], int)
            and isinstance(right_sensor[1], int)
        ), "RunDef: right_sensor must be None or tuple of two ints"
        assert callable(run_action), "RunDef: run must be callable"
        menu.add_item(
            Run(
                display_as,
                color,
                run_action,
                left_sensor,
                right_sensor,
            ),
        )

    # Add motor control
    menu.add_item(Run("C", col.YELLOW, run_motorcontrol))

    # Add exit
    menu.add_item(ActionMenuItem(hub.power_off, "x", col.WHITE))

    # Start Menu
    await menu.loop(
        autoscroll=not cfg.DEBUG_NOSCROLL,
    )

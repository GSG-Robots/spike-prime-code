import gc
import os
import time

import hub

from .gsgr import movement
from .gsgr.config import cfg
from .gsgr.enums import Attachment, Color
from .gsgr.exceptions import StopRun
from .gsgr.menu import ActionMenu
from .gsgr.run import Run


def run_motorcontrol():
    """Motorcontrol"""
    select = 1
    last_select = -1
    motor = Attachment.FRONT_LEFT
    while not hub.button.center.was_pressed():
        if hub.button.left.was_pressed():
            select -= 1
            time.sleep(0.2)
            while hub.button.left.is_pressed():
                time.sleep(0.2)
                select -= 1
        if hub.button.right.is_pressed():
            select += 1
            time.sleep(0.2)
            while hub.button.right.is_pressed():
                time.sleep(0.2)
                select += 1
        if select < 1:
            select = 4
        if select > 4:
            select = 1
        if last_select != select:
            last_select = select
            # mcp.light_up_display(run.brick, motor, 4)
            hub.display.clear()
            if select == 1:
                hub.display.pixel(0, 0, 9)
                motor = Attachment.FRONT_LEFT
            if select == 2:
                hub.display.pixel(4, 0, 9)
                motor = Attachment.FRONT_RIGHT
            if select == 3:
                hub.display.pixel(0, 4, 9)
                motor = Attachment.BACK_LEFT
            if select == 4:
                hub.display.pixel(4, 4, 9)
                motor = Attachment.BACK_RIGHT
    speed = 100
    is_inverted = motor in (Attachment.FRONT_RIGHT, Attachment.BACK_RIGHT)
    hub.display.clear()
    RIGHT_ARROW = hub.Image("09000:09900:09990:09900:09000")
    LEFT_ARROW = hub.Image("00090:00990:09990:00990:00090")
    hub.display.show(RIGHT_ARROW if is_inverted else LEFT_ARROW)
    while not hub.button.center.was_pressed():
        if hub.button.left.is_pressed() and hub.button.right.is_pressed():
            return
        if hub.button.right.is_pressed():
            speed = 100
            hub.display.show(RIGHT_ARROW if is_inverted else LEFT_ARROW)
        if hub.button.left.is_pressed():
            speed = -100
            hub.display.show(LEFT_ARROW if is_inverted else RIGHT_ARROW)
    movement.run_attachment(motor, speed)
    while not hub.button.center.was_pressed():
        time.sleep(0.1)
    movement.stop_attachment()
    time.sleep(1.0)
    raise StopRun


async def main():
    gc.collect()
    mem_perc = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc()) * 100
    print("%s%% of memory used" % mem_perc)
    print("%s%% battery left" % hub.battery.capacity_left())
    print("Voltage:", hub.battery.voltage(), "mV")

    # Reset gear selector
    cfg.GEAR_SELECTOR.preset(cfg.GEAR_SELECTOR.get()[2] + 10)
    cfg.GEAR_SELECTOR.run_to_position(0, speed=100)

    # Align display depending on config
    if cfg.LANDSCAPE:
        hub.display.align(hub.RIGHT)
    else:
        hub.display.align(hub.BACK)

    # Initialize Menu
    menu = ActionMenu(swap_buttons=cfg.LANDSCAPE, focus=cfg.DEBUG_FOCUS)

    # Load runs from runs/*.py
    for file in sorted(os.listdir("/src/runs"), key=str.lower):
        run = getattr(__import__("src.runs.%s" % file[:-4]).runs, file[:-4])
        display_as = run.display_as
        color = run.color
        run_action = run.run
        left_sensor = run.left_sensor if hasattr(run, "left_sensor") else None
        right_sensor = run.right_sensor if hasattr(run, "right_sensor") else None
        assert isinstance(display_as, int) or isinstance(display_as, str), (
            "RunDef: display_as must be str or int"
        )
        assert isinstance(color, int), "RunDef: color must be int"
        assert (
            left_sensor is None
            or isinstance(left_sensor, tuple)
            and len(left_sensor) == 2
            and isinstance(left_sensor[0], int)
            and isinstance(left_sensor[1], int)
        ), "RunDef: left_sensor must be None or tuple of two ints"
        assert (
            right_sensor is None
            or isinstance(right_sensor, tuple)
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
            )
        )

    # Add motor control
    menu.add_item(Run("C", Color.YELLOW, run_motorcontrol))

    # Add exit
    # menu.add_item(ActionMenuItem(menu.exit, "x", Color.WHITE))

    # Start Menu
    await menu.loop(
        autoscroll=not cfg.DEBUG_NOSCROLL,
    )

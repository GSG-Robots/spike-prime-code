import gc
import time

from compyner.typehints import __glob_import__

import gsgr.display
import gsgr.movement
import hub
from gsgr.config import cfg
from gsgr.exceptions import StopRun
from gsgr.menu import ActionMenu, ActionMenuItem
from gsgr.run import Run

FRONT_RIGHT = 2
FRONT_LEFT = 4
BACK_RIGHT = 1
BACK_LEFT = 3


def run_motorcontrol():
    """Motorcontrol"""
    select = 1
    last_select = -1
    motor = FRONT_LEFT
    while not hub.button.center.was_pressed():
        if hub.button.left.is_pressed():
            select -= 1
            hub.button.left.wait_until_released()
            time.sleep(0.1)
        if hub.button.right.is_pressed():
            select += 1
            hub.button.right.wait_until_released()
            time.sleep(0.1)
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
                motor = FRONT_LEFT
            if select == 2:
                hub.display.pixel(4, 0, 9)
                motor = FRONT_RIGHT
            if select == 3:
                hub.display.pixel(0, 4, 9)
                motor = BACK_LEFT
            if select == 4:
                hub.display.pixel(4, 4, 9)
                motor = BACK_RIGHT
    speed = 100
    is_inverted = motor in (FRONT_LEFT, BACK_LEFT, BACK_RIGHT)
    hub.display.clear()
    RIGHT_ARROW = hub.Image("09000:09900:09990:09900:09000")
    LEFT_ARROW = hub.Image("00090:00990:09990:00990:00090")
    hub.display.show_image(RIGHT_ARROW if is_inverted else LEFT_ARROW)
    while not hub.button.center.was_pressed():
        if hub.button.left.is_pressed() and hub.button.right.is_pressed():
            return
        if hub.button.right.is_pressed():
            speed = 100
            hub.display.show_image(RIGHT_ARROW if is_inverted else LEFT_ARROW)
        if hub.button.left.is_pressed():
            speed = -100
            hub.display.show_image(LEFT_ARROW if is_inverted else RIGHT_ARROW)
    gsgr.movement.run_attachment(motor, speed)
    while not hub.button.center.was_pressed():
        time.sleep(0.1)
    gsgr.movement.stop_attachment()
    time.sleep(1.0)
    raise StopRun


def main():
    gc.collect()
    mem_perc = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc()) * 100
    print("%s%% of memory used" % mem_perc)
    print("%s%% battery left" % hub.battery.capacity_left())
    print("Voltage:", hub.battery.voltage(), "mV")

    hub.display.align(hub.RIGHT)
    menu = ActionMenu(swap_buttons=True)

    runs = __glob_import__("runs/*.py")

    for run in runs:
        menu.add_item(
            Run(
                run.get("display_as"),
                run.get("color"),
                # run.get("config"),
                run.get("run"),
            )
        )

    menu.add_item(Run("C", "yellow", run_motorcontrol))

    exit_item = ActionMenuItem(menu.exit, "x", "white")

    menu.add_item(exit_item)

    gsgr.display.show_image(
        (
            (0, 0, 0),
            (0, 0, 0),
            (0, 1, 0),
            (0, 0, 0),
            (0, 0, 0),
        )
    )

    connect_mode = False

    # Reset
    hub.button.center.was_pressed()
    hub.button.connect.was_pressed()

    while hub.battery.charger_detect() in [
        hub.battery.CHARGER_STATE_CHARGING_COMPLETED,
        hub.battery.CHARGER_STATE_CHARGING_ONGOING,
    ]:
        time.sleep(0.2)
        if hub.button.center.was_pressed():
            raise SystemExit
        if hub.button.connect.was_pressed():
            connect_mode = True
            break

    menu.loop(
        autoscroll=True,
        exit_on_charge=cfg.DEBUG_MODE and not connect_mode,
    )


if __name__ == "__main__":
    # <DISABLE BUTTON FOR INTERRUPT>
    callback = hub.button.center.callback()
    hub.button.center.callback(lambda i: ...)
    try:
        main()
    except Exception as e:
        raise e
    finally:
        # Reactivate button callback
        hub.button.center.callback(callback)

    raise SystemExit

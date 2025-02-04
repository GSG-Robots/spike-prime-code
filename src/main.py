import gc
import time

from compyner.typehints import __glob_import__

import gsgr.display
import gsgr.movement
import hub
from gsgr.configuration import config, hardware
from gsgr.menu import ActionMenu, ActionMenuItem
from gsgr.run import Run
from gsgr.utils import DegreeOMeter
from spike import Motor, MotorPair, PrimeHub

FRONT_RIGHT = 2
FRONT_LEFT = 4
BACK_RIGHT = 1
BACK_LEFT = 3


def run_motorcontrol():
    """Motorcontrol"""
    select = 1
    last_select = -1
    motor = FRONT_LEFT
    try:
        while True:
            if hardware.brick.left_button.is_pressed():
                select -= 1
                hardware.brick.left_button.wait_until_released()
                time.sleep(0.1)
            if hardware.brick.right_button.is_pressed():
                select += 1
                hardware.brick.right_button.wait_until_released()
                time.sleep(0.1)
            if select < 1:
                select = 4
            if select > 4:
                select = 1
            if last_select != select:
                last_select = select
                # mcp.light_up_display(run.brick, motor, 4)
                hardware.brick.light_matrix.off()
                if select == 1:
                    hardware.brick.light_matrix.set_pixel(0, 0, 100)
                    motor = FRONT_LEFT
                if select == 2:
                    hardware.brick.light_matrix.set_pixel(4, 0, 100)
                    motor = FRONT_RIGHT
                if select == 3:
                    hardware.brick.light_matrix.set_pixel(0, 4, 100)
                    motor = BACK_LEFT
                if select == 4:
                    hardware.brick.light_matrix.set_pixel(4, 4, 100)
                    motor = BACK_RIGHT
    except KeyboardInterrupt:
        speed = 100
        is_inverted = motor in (FRONT_LEFT, BACK_LEFT, BACK_RIGHT)
        hardware.brick.light_matrix.off()
        hardware.brick.light_matrix.show_image("GO_RIGHT" if is_inverted else "GO_LEFT")
        try:
            while True:
                if (
                    hardware.brick.left_button.is_pressed()
                    and hardware.brick.right_button.is_pressed()
                ):
                    return
                if hardware.brick.right_button.is_pressed():
                    speed = 100
                    hardware.brick.light_matrix.show_image(
                        "GO_RIGHT" if is_inverted else "GO_LEFT"
                    )
                if hardware.brick.left_button.is_pressed():
                    speed = -100
                    hardware.brick.light_matrix.show_image(
                        "GO_LEFT" if is_inverted else "GO_RIGHT"
                    )
        except KeyboardInterrupt:
            try:
                gsgr.movement.run_attachment(motor, speed)
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                gsgr.movement.stop_attachment()
                time.sleep(1.0)


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
                run.get("config"),
                run.get("run"),
            )
        )

    menu.add_item(Run("C", "yellow", {}, run_motorcontrol))

    exit_item = ActionMenuItem(menu.exit, "x", "white")

    menu.add_item(exit_item)

    with (
        hardware(
            drive_shaft=Motor("B"),
            gear_selector=Motor("A"),
            driving_motors=MotorPair("F", "E"),
            left_motor=Motor("F"),
            right_motor=Motor("E"),
            brick=PrimeHub(),
            tire_radius=3,
        ),
        config(
            p_correction=1.2,
            i_correction=0,
            d_correction=-0.5,
            speed_multiplier=1,
            debug_mode=False,
            gyro_tolerance=2,
            degree_o_meter=DegreeOMeter(),
            loop_throttle=0.025,
        ),
    ):
        gsgr.display.show_image(
            (
                (0, 0, 0),
                (0, 0, 0),
                (0, 1, 0),
                (0, 0, 0),
                (0, 0, 0),
            )
        )

        while hub.battery.charger_detect() in [
            hub.battery.CHARGER_STATE_CHARGING_COMPLETED,
            hub.battery.CHARGER_STATE_CHARGING_ONGOING,
        ]:
            time.sleep(0.2)

        menu.loop(autoscroll=True, exit_on_charge=config.debug_mode)


if __name__ == "__main__":
    main()

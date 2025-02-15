import gc
import time

from compyner.typehints import __glob_import__

import gsgr.display
from gsgr.exceptions import StopRun
import gsgr.movement
import hub
from gsgr.configuration import config, hardware, GyroPID
from gsgr.menu import ActionMenu, ActionMenuItem
from gsgr.run import Run
from gsgr.utils import DegreeOMeter
from spike import Motor, MotorPair, PrimeHub, ColorSensor

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
                
    speed = 100
    is_inverted = motor in (FRONT_LEFT, BACK_LEFT, BACK_RIGHT)
    hardware.brick.light_matrix.off()
    hardware.brick.light_matrix.show_image("GO_RIGHT" if is_inverted else "GO_LEFT")
    
    while not hub.button.center.was_pressed():
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
            left_color_sensor=ColorSensor("D"),
            right_color_sensor=ColorSensor("C")
        ),
        config(
            # gyro_drive_pid=GyroPID(1.2, 0.002, -0.7, 2),
            gyro_drive_pid=GyroPID(1.2, 0, -0.7, 2),
            gyro_turn_pid=GyroPID(0.8, 0, -0.1, 2),
            debug_mode=True,
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

        menu.loop(autoscroll=True, exit_on_charge=config.debug_mode and not connect_mode)


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

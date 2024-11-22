import gc
import time

from compyner.typehints import ComPYnerBuildTools

from gsgr.movement import run_attachment, stop_attachment
import hub
from gsgr.configuration import config, hardware
from gsgr.menu import Menu, MenuItem, Run
from gsgr.utils import DegreeOMeter
from spike import Motor, MotorPair, PrimeHub

# gc.enable()
# gc.threshold(round((gc.mem_free() + gc.mem_alloc()) / 20))
gc.collect()
mem_perc = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc()) * 100
print("%s%% of memory used" % mem_perc)

# raise RuntimeError
menu = Menu(landscape=True)

runs = ComPYnerBuildTools.get_modules_path_glob("runs/*.py")

for run in runs:
    menu.add_item(
        Run(run.get("display_as"), run.get("color"), run.get("config"), run.get("run"))
    )
    

FRONT_RIGHT = 3
FRONT_LEFT = 1
BACK_RIGHT = 4
BACK_LEFT = 2


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
                run_attachment(motor, speed)
                while True:
                    time.sleep(0.1)
            except KeyboardInterrupt:
                stop_attachment()
                time.sleep(1.0)

menu.add_item(Run("C", "yellow", {}, run_motorcontrol))

exit_item = MenuItem("x", "white")


@exit_item.set_callback
def exit_callback():
    menu.exit()


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
        p_correction=1.5,
        i_correction=0,
        d_correction=-0.2,
        speed_multiplier=1,
        debug_mode=False,
        gyro_tolerance=2,
        degree_o_meter=DegreeOMeter(),
    ),
):
    hub.display.align(hub.RIGHT)
    menu.loop(autoscroll=True)





# debug_menu = MasterControlProgram(PrimeHub(), DEBUG_MODE)


# @debug_menu.run(display_as="R")
# def restart(run):  # pylint: disable=unused-argument
#     """Restart the robot."""
#     hub.power_off(True, True)


# @debug_menu.run(display_as="D")
# def enbug(run):  # pylint: disable=unused-argument
#     """Disable debug menu."""
#     mcp.defaults["debug_mode"] = False


# while True:
#     try:
#         mcp.start()
#     except BatteryLowError as e:
#         mcp.brick.light_matrix.write("!")
#         mcp.brick.speaker.beep(65, 1)
#         raise e
#     except EnterDebugMenu:
#         try:
#             debug_menu.start(no_debug_menu=True)
#         except SystemExit:
#             continue
#     except Exception as e:
#         mcp.brick.speaker.beep(65, 0.2)
#         time.sleep(0.1)
#         mcp.brick.speaker.beep(70, 0.2)
#         time.sleep(0.1)
#         mcp.brick.speaker.beep(75, 0.1)
#         time.sleep(0.1)
#         mcp.brick.speaker.beep(80, 0.2)
#         mcp.brick.light_matrix.write(str(e))
#         raise e

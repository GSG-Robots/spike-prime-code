from gsgr.menu import Menu, MenuItem, Run
from gsgr.configuration import config, hardware
from gsgr.utils import DegreeOMeter
import hub
from spike import Motor, MotorPair, PrimeHub
from compyner.typehints import ComPYnerBuildTools
import gc

gc.enable()
gc.threshold(round((gc.mem_free() + gc.mem_alloc()) / 20))

mem_perc = gc.mem_alloc() / (gc.mem_free() + gc.mem_alloc()) * 100
print("%s%% of memory used" % mem_perc)

# raise RuntimeError
menu = Menu(landscape=True)

runs = ComPYnerBuildTools.get_modules_path_glob("runs/*.py")

for run in runs:
    menu.add_item(
        Run(run.get("display_as"), run.get("color"), run.get("config"), run.get("run"))
    )

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
        error_threshold=1,
        degree_offset=0,
        gyro_tolerance=1,
        degree_o_meter=DegreeOMeter(),
    ),
):
    hub.display.align(hub.RIGHT)
    menu.loop(autoscroll=True)


# @mcp.run(display_as="C", debug_mode=False)
# def run_motorcontrol(run: Run):
#     """Motorcontrol"""
#     select = 1
#     last_select = -1
#     motor = FRONT_RIGHT
#     try:
#         while True:
#             if run.brick.left_button.is_pressed():
#                 select -= 1
#                 run.brick.left_button.wait_until_released()
#                 time.sleep(0.1)
#             if run.brick.right_button.is_pressed():
#                 select += 1
#                 run.brick.right_button.wait_until_released()
#                 time.sleep(0.1)
#             if select < 1:
#                 select = 4
#             if select > 4:
#                 select = 1
#             if last_select != select:
#                 last_select = select
#                 # mcp.light_up_display(run.brick, motor, 4)
#                 mcp.brick.light_matrix.off()
#                 if select == 1:
#                     mcp.brick.light_matrix.set_pixel(0, 0, 100)
#                     motor = FRONT_LEFT
#                 if select == 2:
#                     mcp.brick.light_matrix.set_pixel(4, 0, 100)
#                     motor = FRONT_RIGHT
#                 if select == 3:
#                     mcp.brick.light_matrix.set_pixel(0, 4, 100)
#                     motor = BACK_LEFT
#                 if select == 4:
#                     mcp.brick.light_matrix.set_pixel(4, 4, 100)
#                     motor = BACK_RIGHT
#     except KeyboardInterrupt:
#         speed = 100
#         is_inverted = motor in (BACK_RIGHT, FRONT_RIGHT)
#         mcp.brick.light_matrix.off()
#         mcp.brick.light_matrix.show_image("GO_RIGHT" if is_inverted else "GO_LEFT")
#         try:
#             while True:
#                 if (
#                     run.brick.left_button.is_pressed()
#                     and run.brick.right_button.is_pressed()
#                 ):
#                     return
#                 if run.brick.right_button.is_pressed():
#                     speed = 100
#                     mcp.brick.light_matrix.show_image(
#                         "GO_RIGHT" if is_inverted else "GO_LEFT"
#                     )
#                 if run.brick.left_button.is_pressed():
#                     speed = -100
#                     mcp.brick.light_matrix.show_image(
#                         "GO_LEFT" if is_inverted else "GO_RIGHT"
#                     )
#         except KeyboardInterrupt:
#             try:
#                 run.drive_attachment(motor, speed)
#                 while True:
#                     time.sleep(0.1)
#             except KeyboardInterrupt:
#                 run.drive_shaft.stop()
#                 time.sleep(1.0)


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

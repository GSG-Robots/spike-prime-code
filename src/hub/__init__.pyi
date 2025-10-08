"""
LEGO provided functions and values.
"""

from typing import Any, overload

from . import battery, bluetooth, button, display, port, motion
from .port import Motor, MotorPair

TOP = 0
"The top of the hub. This is the side with the matrix display."

FRONT = 1
"The front of the hub. This is the side with the USB port."

RIGHT = 2
"The right side of the hub. This is the side with ports B, D, and F."

BOTTOM = 3
"The bottom side of the hub. This is the side of the battery compartment."

BACK = 4
"The back side of the hub. This is the side with the speaker."

LEFT = 5
"The left side of the hub. This is the side with ports A, C, and E."

__version__: str
"""
The firmware version of the form 'v1.0.06.0034-b0c335b', consisting of the components:

v major . minor . bugfix . build - hash.
"""

config: dict
"""
Dictionary of hub configuration variables.

You can override its default values in ``boot.py`` or add your own entries. This dictionary is accessible to all of your programs until you reboot the hub.

The values in ``hub.config[]`` are evaluated in the following order of increasing priority:

1. Default value as described below. Note that there will be no corresponding entry in ``hub.config[]``

2. If the file ``/etc/hub_config`` exists and has no syntax errors then it is evaluated and may update or create values in ``hub.config[]``.

3. If the file ``boot.py`` exists and has no syntax errors then it is evaluated and may update or create values in ``hub.config[]``. After evaluating ``boot.py`` the one-time post boot initialization happens.

4. If the file ``main.py`` exists and has no syntax errors then it is evaluated and may update or create values in ``hub.config[]``.

5. Any user supplied file or console commands may override an entry in ``hub.config[]``.

By default ``hub.config[]`` has the following entries:

* ``hostname``: Identifies the hub in various places such as Bluetooth advertising. This value is read from ``/etc/hostname``.

* ``lwp_advertise``: Configures whether the firmware should control BLE advertising using the LEGO Wireless Protocol. A positive value enables advertising after the given duration (ms) after boot. Set to 0 to disable advertising.

* ``bt_discoverable``: Configures whether the hub should be discoverable with Bluetooth classic. A positive value makes it discoverable after the given duration after boot. Set to 0 to disable discoverability.

* ``disconnect_behavior_enabled``: If ``True``, hub shuts down automatically after some time if no Bluetooth connection is made.

* ``lwp_bypass``: If ``True``, the firmware will not process LEGO Wireless Protocol commands. It is False by default.

* ``disable_usb_poweron``: If this key exists, the hub will not start up again if USB is connected after shutdown.

* ``powerdown_timeout``: Sets the inactivity timeout (ms) before the hub shuts down. Set to ``0`` to disable automatic shutdown.

* ``device_get_can_return_float``: Configures whether a device (sensor or motor) returns an integer or float as a result of executing the ``get()`` method. Default value is ``False``.
"""

def info() -> dict[str, int | str]:
    """
    Gets a dictionary of the form:
    ```json
    {
        # System performance information.
        '1ms_tick_min': 329000.0,
        '1ms_tick_on_time': 99.9991,
        '1ms_tick_miss': 131,
        '1ms_tick_max': 7.32e+06,
        '1ms_tick_total': 14702993,

        # Product variant.
        # Other = 0
        # MINDSTORMS Inventor Hub = 1
        'product_variant': 1,

        # PCB version.
        'hardware_version': 'Version_E',

        # Unique identifier of your hub.
        'device_uuid': '03970000-3B00-3B00-1451-383332353732'
    }
    ```

    Returns: Hub information dictionary similar to the example above.
    """
    ...

def status() -> dict[str, Any]:
    """
    Gets the state of internal sensors, external devices, and the display.

    This gives a dictionary equivalent to:

    ```
    {
        'gyroscope': motion.gyroscope(),
        'position': motion.position(),
        'accelerometer': motion.accelerometer(),
        'port': {
            'A': port.A.get(),
            'B': port.B.get(),
            'C': port.C.get(),
            'D': port.D.get(),
            'E': port.E.get(),
            'F': port.F.get(),
        },
        'display': display.show()
    }
    ```
    Further details can be obtained on the ``hub.motion``, ``hub.display``, and ``Port`` pages.

    Returns: Status dictionary as given above.
    """
    ...

@overload
def power_off(fast: bool = True, restart: bool = False) -> None: ...
@overload
def power_off(timeout: int = 0) -> None:
    """
    Sets a timeout to turn the hub off after inactivity.

    Keyword Arguments:
        timeout: Sets the inactivity timeout before the hub shuts down automatically.
    """
    ...

def repl_restart(restart: bool | None = None) -> None:
    """
    Resets the REPL and clears all variables.

    Parameters:
        restart: Select ``True`` to restart. If this argument is ``False`` or not given at all, nothing happens.
    """
    ...

def temperature() -> float:
    """
    Gets the temperature of the hub.

    Returns: Temperature in degrees Celsius.
    """
    ...

@overload
def led(color: int) -> None: ...
@overload
def led(red: int, green: int, blue: int) -> None: ...
@overload
def led(color: tuple[int, int, int]) -> None:
    """
    Sets the color of the LED in the center button of the hub.

    Parameters:
        color:
            Choose one of these formats:

            * Color code:
                * 0 = off
                * 1 = pink
                * 2 = violet
                * 3 = blue
                * 4 = turquoise
                * 5 = light green
                * 6 = green
                * 7 = yellow
                * 8 = orange
                * 9 = red
                * 10 = white
                * Any other value gives dim white light.
            * RGB mode: You provide the intensity for red, green, and blue light separately. Each value must be between ``0`` and ``255``.
            * Tuple mode. This works just like RGB mode, but you can provide all three values in a single tuple.
    """

def file_transfer(filename: str, filesize: int, packetsize: int = 1000, timeout: int = 2000, mode=None) -> None:
    """
    Prepares a file transfer to the hub.

    After calling this function, press ``CTRL+F`` or send ``\x06`` to start the actual transfer. Bytes sent after this will be written to the specified file on the hub. Once the transfer is complete or fails, the REPL resumes control.

    Auto-detection of transfer interface (USB or Bluetooth) is enabled. The first interface that receives a good package within the specified timeout, will be used for the rest of the transfer.

    Parameters
        filename: Absolute path to the file. The containing folder must already exist.

        filesize: Size of the file to be transferred, expressed as a number of bytes. The size must not exceed the remaining amount of storage space.

        packetsize: Size of each packet. The packet is not written until it is received in full.

        mode: String with optional file transfer settings. Choose ``'a'`` to make the hub send ``ACK`` or ``NAK`` after each packet. Doing so is recommended for USB transfers but not for Bluetooth Classic transfers.

    Raises
        OSError (ETIMEDOUT): If the transfer was started but the expected data was not received within the timeout.
    """

class Image:
    ANGRY: Image
    ARROW_E: Image
    ARROW_N: Image
    ARROW_NE: Image
    ARROW_NW: Image
    ARROW_S: Image
    ARROW_SE: Image
    ARROW_SW: Image
    ARROW_W: Image
    ASLEEP: Image
    BUTTERFLY: Image
    CHESSBOARD: Image
    CLOCK1: Image
    CLOCK2: Image
    CLOCK3: Image
    CLOCK4: Image
    CLOCK5: Image
    CLOCK6: Image
    CLOCK7: Image
    CLOCK8: Image
    CLOCK9: Image
    CLOCK10: Image
    CLOCK11: Image
    CLOCK12: Image
    CONFUSED: Image
    COW: Image
    DIAMOND: Image
    DIAMOND_SMALL: Image
    DUCK: Image
    FABULOUS: Image
    GHOST: Image
    GIRAFFE: Image
    GO_DOWN: Image
    GO_LEFT: Image
    GO_RIGHT: Image
    GO_UP: Image
    HAPPY: Image
    HEART: Image
    HEART_SMALL: Image
    HOUSE: Image
    MEH: Image
    MUSIC_CROTCHET: Image
    MUSIC_QUAVER: Image
    MUSIC_QUAVERS: Image
    NO: Image
    PACMAN: Image
    PITCHFORK: Image
    RABBIT: Image
    ROLLERSKATE: Image
    SAD: Image
    SILLY: Image
    SKULL: Image
    SMILE: Image
    SNAKE: Image
    SQUARE: Image
    SQUARE_SMALL: Image
    STICKFIGURE: Image
    SURPRISED: Image
    SWORD: Image
    TARGET: Image
    TORTOISE: Image
    TRIANGLE: Image
    TRIANGLE_LEFT: Image
    TSHIRT: Image
    UMBRELLA: Image
    XMAS: Image
    YES: Image
    ALL_CLOCKS: tuple[Image]
    ALL_ARROWS: tuple[Image]

    @overload
    def __init__(self, image: str): ...
    @overload
    def __init__(self, width: int, height: int): ...
    @overload
    def __init__(self, width: int, height: int, buffer: bytes): ...
    def width(self) -> int: ...
    def height(self) -> int: ...
    def shift_left(self, n: int) -> Image: ...
    def shift_right(self, n: int) -> Image: ...
    def shift_up(self, n: int) -> Image: ...
    def shift_down(self, n: int) -> Image: ...
    def get_pixel(self, x: int, y: int) -> int: ...
    def set_pixel(self, x: int, y: int, brightness: int) -> None: ...

__all__ = [
    "battery",
    "bluetooth",
    "button",
    "display",
    "motion",
    "port",
    "Motor",
    "MotorPair",
    "TOP",
    "FRONT",
    "RIGHT",
    "BOTTOM",
    "BACK",
    "LEFT",
    "__version__",
    "config",
    "info",
    "status",
    "power_off",
    "repl_restart",
    "temperature",
    "led",
    "file_transfer",
    "Image",
]

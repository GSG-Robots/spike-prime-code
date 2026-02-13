import asyncio
import time

import color
import hub

# in mV
PERFECT_VOLTAGE = 8300
OK_VOLTAGE = 8250
LOW_VOLTAGE = 7850

# in ms
SCREEN_TIMEOUT = 10000
CHARGING_TIMEOUT = 100
FULL_TIMEOUT = 500

POWER_OFF_WHEN_NOT_CHARGING_FOR = 60000
ALERT_LOUDER_WHEN_NOT_CHARGING_FOR = 20000
ALERT_WHEN_NOT_CHARGING_FOR = 5000

ALERT_LOUDER_WHEN_FULL_FOR = 20000
ALERT_WHEN_FULL_FOR = 5000

BLINKING_INTERVAL = 200


def render_percentage(percentage: float):
    for y in range(5):
        if percentage >= (y + 1) * 20:
            hub.light_matrix.set_pixel(2, y, 100)
        elif percentage >= (y + 0.5) * 20:
            hub.light_matrix.set_pixel(2, y, 50)
        else:
            hub.light_matrix.set_pixel(2, y, 0)
    return


class TimingOutBoolean:
    def __init__(self):
        self.last_true = 0

    def set_current(self, value: bool):
        if value:
            self.last_true = time.ticks_ms()

    def in_the_last(self, timeout_ms: int) -> bool:
        return time.ticks_diff(time.ticks_ms(), self.last_true) < timeout_ms


async def battery():
    IN_USE = TimingOutBoolean()
    CHARGING = TimingOutBoolean()
    FULL = TimingOutBoolean()

    was_charging = False

    while not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT)):
        # Read current battery voltage and USB charge current
        tm = time.ticks_ms()
        vt = hub.battery_voltage()
        ct = hub.usb_charge_current()

        # Calculate basic battery status
        low_voltage_reached = vt >= LOW_VOLTAGE
        ok_voltage_reached = vt >= OK_VOLTAGE
        perfect_voltage_reached = vt >= PERFECT_VOLTAGE
        percentage: float = min(100, (
            (vt - LOW_VOLTAGE) / (OK_VOLTAGE - LOW_VOLTAGE) * 100 if low_voltage_reached else vt / LOW_VOLTAGE * 100
        ))

        # Update timing out booleans
        CHARGING.set_current(ct > 10)
        FULL.set_current(perfect_voltage_reached)
        IN_USE.set_current(
            bool(
                hub.button.pressed(hub.button.POWER)
                or hub.button.pressed(hub.button.LEFT)
                or hub.button.pressed(hub.button.RIGHT),
            ),
        )

        # Base cases for timeout values
        is_full = FULL.in_the_last(FULL_TIMEOUT)
        is_charging = CHARGING.in_the_last(CHARGING_TIMEOUT)
        is_in_use = IN_USE.in_the_last(SCREEN_TIMEOUT)

        # Set power LED color based on voltage level
        if perfect_voltage_reached:
            hub.light.color(hub.light.POWER, color.BLUE)
        elif ok_voltage_reached:
            hub.light.color(hub.light.POWER, color.GREEN)
        elif low_voltage_reached:
            hub.light.color(hub.light.POWER, color.YELLOW)
        else:
            hub.light.color(hub.light.POWER, color.RED)

        if is_charging and not was_charging:
            was_charging = True
            IN_USE.set_current(True)
            hub.sound.beep(400, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(40)
            hub.sound.beep(800, 35, 50, waveform=hub.sound.WAVEFORM_SINE)

        elif not is_charging and was_charging:
            was_charging = False
            hub.sound.beep(600, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(40)
            hub.sound.beep(400, 35, 50, waveform=hub.sound.WAVEFORM_SINE)

        if is_in_use:
            render_percentage(percentage)
        elif is_charging:
            hub.light_matrix.clear()
        elif not is_full:
            # Blink plug when not charging
            if (tm // BLINKING_INTERVAL) % 2 == 0:
                hub.light_matrix.set_pixel(1, 0, 100)
                hub.light_matrix.set_pixel(2, 0, 0)
                hub.light_matrix.set_pixel(3, 0, 100)

                for i in range(5):
                    hub.light_matrix.set_pixel(i, 1, 100)
                    hub.light_matrix.set_pixel(i, 2, 100)

                hub.light_matrix.set_pixel(1, 3, 100)
                hub.light_matrix.set_pixel(2, 3, 100)
                hub.light_matrix.set_pixel(3, 3, 100)

                hub.light_matrix.set_pixel(2, 4, 100)
                hub.light.color(hub.light.POWER, color.ORANGE)
            else:
                hub.light_matrix.clear()
                hub.light.color(hub.light.POWER, color.BLACK)

        # Power off when not charging for a long time
        if not CHARGING.in_the_last(POWER_OFF_WHEN_NOT_CHARGING_FOR):
            hub.power_off()

        # Skip alerting when the battery is full but not charging
        elif not is_charging and is_full:
            ...

        # Alert when not charging
        elif not CHARGING.in_the_last(ALERT_LOUDER_WHEN_NOT_CHARGING_FOR):
            hub.sound.beep(1500, 35, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
        elif not CHARGING.in_the_last(ALERT_WHEN_NOT_CHARGING_FOR):
            hub.sound.beep(1000, 35, 60, waveform=hub.sound.WAVEFORM_SINE)

        # Alert when full if charging
        elif FULL.in_the_last(ALERT_LOUDER_WHEN_FULL_FOR):
            hub.sound.beep(800, 70, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
            await asyncio.sleep_ms(75)
            hub.sound.beep(1000, 70, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
            await asyncio.sleep_ms(75)
            hub.sound.beep(1200, 100, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
            await asyncio.sleep_ms(55)
        elif FULL.in_the_last(ALERT_WHEN_FULL_FOR):
            hub.sound.beep(800, 70, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(75)
            hub.sound.beep(1000, 70, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(75)
            hub.sound.beep(1200, 100, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(55)

        await asyncio.sleep_ms(50)

    hub.light_matrix.clear()

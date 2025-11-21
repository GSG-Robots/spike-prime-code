import asyncio
import time

import color
import hub

# in mV
MAX_VOLTAGE = 8250
MIN_VOLTAGE = 7850
# in ms
SCREEN_TIMEOUT = 10000


def render_percentage(percentage: float):
    for y in range(5):
        if percentage >= (y + 1) * 20:
            hub.light_matrix.set_pixel(2, y, 100)
        elif percentage >= (y + 0.5) * 20:
            hub.light_matrix.set_pixel(2, y, 50)
        else:
            hub.light_matrix.set_pixel(2, y, 0)
    return


async def battery():
    LAST_USED = time.ticks_ms()
    WAS_CHARGING = False
    LAST_CHARGING = time.ticks_ms()
    MAX_VOLTAGE_REACHED = 00

    while not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT)):
        vt = hub.battery_voltage()
        is_charging = hub.usb_charge_current() > 10
        min_voltage_reached = vt >= MIN_VOLTAGE
        max_voltage_reached = vt >= MAX_VOLTAGE
        percentage: float = (
            (vt - MIN_VOLTAGE) / (MAX_VOLTAGE - MIN_VOLTAGE) * 100 if min_voltage_reached else vt / MIN_VOLTAGE * 100
        )

        if not max_voltage_reached:
            MAX_VOLTAGE_REACHED = 0

        if max_voltage_reached:
            MAX_VOLTAGE_REACHED += 1
            hub.light.color(hub.light.POWER, color.GREEN)
            if is_charging:
                volume = min(MAX_VOLTAGE_REACHED * 3 + 20, 100)
                not_yet_angry = (
                    MAX_VOLTAGE_REACHED < 40 or MAX_VOLTAGE_REACHED % (max(1, 10 - MAX_VOLTAGE_REACHED // 10)) != 0
                )
                waveform = hub.sound.WAVEFORM_SINE if not_yet_angry else hub.sound.WAVEFORM_SAWTOOTH
                hub.sound.beep(400, 100, volume, waveform=waveform)
                await asyncio.sleep_ms(100)
                hub.sound.beep(500, 100, volume, waveform=waveform)
                await asyncio.sleep_ms(100)
                hub.sound.beep(700, 120, volume, waveform=waveform)
                await asyncio.sleep_ms(400)
        elif min_voltage_reached:
            hub.light.color(hub.light.POWER, color.YELLOW)
        else:
            hub.light.color(hub.light.POWER, color.RED)

        if (
            hub.button.pressed(hub.button.POWER)
            or hub.button.pressed(hub.button.LEFT)
            or hub.button.pressed(hub.button.RIGHT)
        ):
            LAST_USED = time.ticks_ms()

        if is_charging:
            LAST_CHARGING = time.ticks_ms()

        if is_charging and not WAS_CHARGING:
            WAS_CHARGING = True
            LAST_USED = time.ticks_ms() - 5000
            hub.sound.beep(400, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(40)
            hub.sound.beep(800, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
        elif not is_charging and WAS_CHARGING:
            WAS_CHARGING = False
            hub.sound.beep(600, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
            await asyncio.sleep_ms(40)
            hub.sound.beep(400, 35, 50, waveform=hub.sound.WAVEFORM_SINE)

        if is_charging:
            if time.ticks_ms() < LAST_USED + SCREEN_TIMEOUT:
                render_percentage(percentage)
            else:
                hub.light_matrix.clear()
        else:
            hub.light_matrix.set_pixel(2, 0, 100)
            hub.light_matrix.set_pixel(2, 1, 100)
            hub.light_matrix.set_pixel(2, 2, 100)
            hub.light_matrix.set_pixel(2, 3, 0)
            hub.light_matrix.set_pixel(2, 4, 100)

        if time.ticks_ms() > LAST_USED + SCREEN_TIMEOUT:
            if time.ticks_ms() > LAST_CHARGING + 45000:
                hub.power_off()
            elif time.ticks_ms() > LAST_CHARGING + 40000:
                hub.sound.beep(1500, 100, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
            elif time.ticks_ms() > LAST_CHARGING + 30000:
                hub.sound.beep(1000, 35, 100, waveform=hub.sound.WAVEFORM_SAWTOOTH)
            elif time.ticks_ms() > LAST_CHARGING + 10000:
                hub.sound.beep(1000, 35, 50, waveform=hub.sound.WAVEFORM_SINE)
            elif time.ticks_ms() > LAST_CHARGING + 2000:
                hub.sound.beep(1000, 35, 10, waveform=hub.sound.WAVEFORM_SINE)

        await asyncio.sleep_ms(50)

    hub.light_matrix.clear()

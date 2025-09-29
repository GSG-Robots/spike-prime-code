import time
import hub
import asyncio
import color


async def battery():
    intensity: int = 100
    lvl: int | float = 0
    last_used = {"time": time.ticks_ms()}

    while hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT):
        return

    async def watch_button():
        while True:
            if hub.button.pressed(hub.button.POWER) or hub.button.pressed(hub.button.LEFT) or hub.button.pressed(hub.button.RIGHT):
                last_used["time"] = time.ticks_ms()

            await asyncio.sleep_ms(100)

    task = asyncio.create_task(watch_button())
    try:
        while not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT)):
            vt = hub.battery_voltage()
            if vt < 7850:
                lvl = (vt / 7850) * 100
                intensity = 50
            else:
                lvl = ((vt - 7850) / 450) * 100
                intensity = 100

            if last_used["time"] + 10000 > time.ticks_ms() or lvl >= 99:
                if intensity == 50:
                    hub.light.color(hub.light.POWER, color.RED)

                if intensity == 100:
                    hub.light.color(hub.light.POWER, color.YELLOW)
                    if lvl >= 99:
                        hub.light.color(hub.light.POWER, color.GREEN)
                        hub.sound.beep(400, 100, 90)

                if lvl > 9:
                    hub.light_matrix.set_pixel(2, 0, intensity // 2)
                await asyncio.sleep_ms(100)
                if lvl > 19:
                    hub.light_matrix.set_pixel(2, 0, intensity)
                await asyncio.sleep_ms(100)
                if lvl > 29:
                    hub.light_matrix.set_pixel(2, 1, intensity // 2)
                await asyncio.sleep_ms(100)
                if lvl > 39:
                    hub.light_matrix.set_pixel(2, 1, intensity)
                await asyncio.sleep_ms(100)
                if lvl > 49:
                    hub.light_matrix.set_pixel(2, 2, intensity // 2)
                await asyncio.sleep_ms(100)
                if lvl > 59:
                    hub.light_matrix.set_pixel(2, 2, intensity)
                await asyncio.sleep_ms(100)
                if lvl > 69:
                    hub.light_matrix.set_pixel(2, 3, intensity // 2)
                await asyncio.sleep_ms(100)
                if lvl > 79:
                    hub.light_matrix.set_pixel(2, 3, intensity)
                await asyncio.sleep_ms(100)
                if lvl > 89:
                    hub.light_matrix.set_pixel(2, 4, intensity // 2)
                await asyncio.sleep_ms(100)
                if lvl > 99:
                    hub.light_matrix.set_pixel(2, 4, intensity)
                await asyncio.sleep_ms(100)
                if lvl <= 89:
                    hub.light_matrix.set_pixel(2, 4, 0)
                if lvl <= 69:
                    hub.light_matrix.set_pixel(2, 3, 0)
                if lvl <= 49:
                    hub.light_matrix.set_pixel(2, 2, 0)
                if lvl <= 29:
                    hub.light_matrix.set_pixel(2, 1, 0)
                if lvl <= 9:
                    hub.light_matrix.set_pixel(2, 0, 10)
            else:
                hub.light_matrix.clear()
                hub.light.color(hub.light.POWER, color.BLACK)

            while hub.usb_charge_current() < 10:
                if hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT):
                    return
                await asyncio.sleep_ms(100)

            await asyncio.sleep_ms(100)
    finally:
        task.cancel()
    hub.light_matrix.clear()

import asyncio

import color
import hub

TARGET = [
    100,
    100,
    100,
    100,
    100,
    100,
    0,
    0,
    0,
    100,
    100,
    0,
    100,
    0,
    100,
    100,
    0,
    0,
    0,
    100,
    100,
    100,
    100,
    100,
    100,
]
TARGET_INVERSE = [
    0,
    0,
    0,
    0,
    0,
    0,
    100,
    100,
    100,
    0,
    0,
    100,
    0,
    100,
    0,
    0,
    100,
    100,
    100,
    0,
    0,
    0,
    0,
    0,
    0,
]


async def bg_task():
    while True:
        hub.light.color(hub.light.POWER, color.GREEN)
        hub.sound.beep(400, 225, 100)
        hub.light_matrix.show(TARGET)
        await asyncio.sleep_ms(250)
        hub.light.color(hub.light.POWER, color.RED)
        hub.sound.beep(500, 225, 100)
        await asyncio.sleep_ms(250)
        hub.light.color(hub.light.POWER, color.BLUE)
        hub.sound.beep(600, 225, 100)
        hub.light_matrix.show(TARGET_INVERSE)
        await asyncio.sleep_ms(250)
        hub.light.color(hub.light.POWER, color.YELLOW)
        hub.sound.beep(700, 225, 100)
        await asyncio.sleep_ms(250)


async def loop():
    task = asyncio.create_task(bg_task())
    try:
        while True:
            if hub.button.pressed(hub.button.POWER):
                break
            await asyncio.sleep_ms(100)
    finally:
        task.cancel()

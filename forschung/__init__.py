import asyncio

import hub
import motor


async def loop():
    try:
        running = True
        motor.run(hub.port.F, 1000)
        while True:
            if hub.button.pressed(hub.button.POWER):
                running = not running
                if running:
                    motor.run(hub.port.F, 1000)
                else:
                    motor.stop(hub.port.F, stop=motor.COAST)
                while hub.button.pressed(hub.button.POWER):
                    await asyncio.sleep_ms(75)
            await asyncio.sleep_ms(75)
    except asyncio.CancelledError:
        motor.stop(hub.port.F, stop=motor.COAST)

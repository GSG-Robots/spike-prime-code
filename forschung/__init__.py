import hub
import motor
import asyncio


async def loop():
    try:
        running = True
        motor.run(hub.port.A, 1000)
        while True:
            if hub.button.pressed(hub.button.POWER):
                running = not running
                if running:
                    motor.run(hub.port.A, 1000)
                else:
                    motor.stop(hub.port.A, stop=motor.COAST)
                while hub.button.pressed(hub.button.POWER):
                    await asyncio.sleep_ms(75)
            await asyncio.sleep_ms(75)
    except asyncio.CancelledError:
        motor.stop(hub.port.A, stop=motor.COAST)

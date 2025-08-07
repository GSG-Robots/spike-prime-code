import spielzeug
import uasyncio as asyncio


def start():
    asyncio.run(spielzeug.main_loop())

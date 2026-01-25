import device

from .battery import battery


async def loop():
    while not (device.ready(2) and device.ready(3)):
        await battery()

    from .main import main

    await main()


__all__ = ["loop"]

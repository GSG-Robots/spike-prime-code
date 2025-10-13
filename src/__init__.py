import device


async def loop():
    from .battery import battery

    while not (device.ready(2) and device.ready(3)):
        await battery()

    from .main import main

    await main()


__all__ = ["loop"]

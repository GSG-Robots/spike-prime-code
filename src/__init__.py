from .main import main

async def loop():
    await main()


__all__ = ["loop"]

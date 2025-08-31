from .main import main


async def loop():
    try:
        await main()
    finally:
        remote.unblock()


__all__ = ["loop"]

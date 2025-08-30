from .main import main


async def loop():
    try:
        await main()
    except Exception as e:
        remote.error(e)
        remote.unblock()


__all__ = ["loop"]

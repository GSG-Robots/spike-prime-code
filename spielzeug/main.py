import hub
import micropython
import uasyncio as asyncio
import server

micropython.alloc_emergency_exception_buf(256)


if not (
    hub.button.pressed(hub.button.CONNECT)
    and hub.button.pressed(hub.button.LEFT)
    and hub.button.pressed(hub.button.RIGHT)
):
    asyncio.run(server.main())
else:
    hub.sound.beep(600, 1000)

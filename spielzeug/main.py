import micropython
import uasyncio as asyncio

micropython.alloc_emergency_exception_buf(256)

import hub

if not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT) and hub.button.pressed(hub.button.CONNECT)):
    import server
    asyncio.run(server.main())

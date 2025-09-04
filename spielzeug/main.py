import micropython
import server
import uasyncio as asyncio

micropython.alloc_emergency_exception_buf(256)

import hub

if not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT)):
    asyncio.run(server.main())

import micropython
import asyncio

import hub

micropython.alloc_emergency_exception_buf(256)


if not (hub.button.pressed(hub.button.LEFT) and hub.button.pressed(hub.button.RIGHT) and hub.button.pressed(hub.button.CONNECT)):
    import server

    asyncio.run(server.main())

import micropython
import uasyncio as asyncio
import server

micropython.alloc_emergency_exception_buf(256)

asyncio.run(server.main())

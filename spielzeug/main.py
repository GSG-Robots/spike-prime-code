import micropython
import server
import uasyncio as asyncio
from bleio import BLEIO

micropython.alloc_emergency_exception_buf(256)


asyncio.run(server.main())

# import hub
import micropython
from bleio import BLEIO
# import uasyncio as asyncio
import server

micropython.alloc_emergency_exception_buf(256)


server.register_packets()
BLEIO.start_advertising()

import micropython
import uasyncio as asyncio
import spielzeug

micropython.alloc_emergency_exception_buf(256)

asyncio.run(spielzeug.main_loop())

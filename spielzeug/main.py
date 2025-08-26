import micropython
import uasyncio as asyncio
import os

print(os.listdir("/flash/flash/src"))
import src

micropython.alloc_emergency_exception_buf(256)

asyncio.run(src.loop())

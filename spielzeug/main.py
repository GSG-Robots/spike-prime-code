import gc

import micropython
import uasyncio as asyncio

import spielzeug

gc.enable()
gc.collect()
micropython.alloc_emergency_exception_buf(256)

asyncio.run(spielzeug.main_loop())

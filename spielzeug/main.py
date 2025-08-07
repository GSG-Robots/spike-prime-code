import gc
import micropython

import custom_runtime

micropython.alloc_emergency_exception_buf(256)

custom_runtime.start()

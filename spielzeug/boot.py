import micropython

import hub

micropython.alloc_emergency_exception_buf(128)

hub.config["hub_os_enable"] = False
hub.config["hub_os_auto_advertise"] = False

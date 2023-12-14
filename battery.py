# LEGO type:standard slot:9 autostart
"""Short run to show battery state"""

import hub
import spike

CAPACITY = hub.battery.capacity_left()
MSG = str(CAPACITY) + "%"
spike.PrimeHub().light_matrix.write(MSG)

raise SystemExit

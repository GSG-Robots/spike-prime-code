"""Short run to show battery state"""

import hub # type: ignore # pylint: disable=import-error
import spike

while True:
    CAPACITY = hub.battery.capacity_left()
    MSG = str(CAPACITY)+"%"
    spike.PrimeHub().light_matrix.write(MSG)

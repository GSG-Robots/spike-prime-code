import time
import hub
import spike

hb = spike.PrimeHub()

while True:
    hb.light_matrix.write((hub.battery.voltage() - 8000) // 3)
    time.sleep(1)

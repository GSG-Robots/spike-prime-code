# LEGO type:standard slot:3 autostart
import time
import spike

a = spike.Motor("B")

a.run_to_position(81, speed=50)
time.sleep(1)
a.run_to_position(261, speed=50)
time.sleep(1)
a.run_to_position(351, speed=50)
time.sleep(1)
a.run_to_position(171, speed=50)

a.run_to_position(171, speed=50)
time.sleep(1)
a.run_to_position(351, speed=50)
time.sleep(1)
a.run_to_position(261, speed=50)
time.sleep(1)
a.run_to_position(81, speed=50)
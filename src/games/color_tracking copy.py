# LEGO type:standard slot:10 autostart
import time
import hub

color_sensor = hub.port.C.device
color_sensor2 = hub.port.D.device
time.sleep(0.3)
color_sensor.mode(3)
color_sensor2.mode(3)
time.sleep(0.3)

phase = 0
bright = [9, 0, 0]
while not hub.button.left.is_pressed():
    if bright[phase] == 0:
        phase += 1
        phase %= 3
    bright[phase] -= 1
    bright[(phase + 1) % 3] += 1
    color_sensor.mode(3, bytes(tuple(bright)))
    color_sensor2.mode(3, bytes(reversed(tuple(bright))))
    time.sleep(0.04)

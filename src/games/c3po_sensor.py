# LEGO type:standard slot:11 autostart
import time
import hub

color_sensor = hub.port.A.device
color_sensor.mode((5, 1))
time.sleep(0.3)


order = [
    ((500, 1025), (500, 1025), (500, 1025)),  # Grenzwerte -> weiß     0
    ((0, 500), (0, 500), (0, 500)),  # Grenzwerte -> schwarz  1
    ((500, 1024), (0, 500), (0, 500)),  # Grenzwerte -> rot      2
]

def current_state(r, g, b):
    for index, (rx, gx, bx) in enumerate(order):
        if rx[0] < r < rx[1] and gx[0] < g < gx[1] and bx[0] < b < bx[1]:
            return index

    return None



brightness, color, r, g, b = color_sensor.get()
last_state = current_state(r, g, b)
counter = 0

while not hub.button.left.is_pressed():
    brightness, color, r, g, b = color_sensor.get()
    # print(brightness, color, r, g, b)
    _current_state = current_state(r, g, b)
    # print(_current_state)
    # time.sleep(1)
    if last_state != _current_state and _current_state is not None:
        print("Laststate: ", last_state, "_current_state: ", _current_state)

        # if last_state < _current_state  or (last_state == 2 and _current_state == 0) and (last_state != 0):
        #     counter += 1
        #     print("Plus 1")

        # elif last_state > _current_state  or (last_state == 0 and _current_state == 2):
        #     counter -= 1
        #     print("Minus 1")

        if last_state == ((_current_state - 1) % 3):
            counter += 1
            print("Plus 1")

        elif last_state == ((_current_state + 1) % 3):
            counter -= 1
            print("Minus 1")

        print(counter)
        last_state = _current_state


# Todo: add counting system

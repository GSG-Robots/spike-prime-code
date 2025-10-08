# LEGO type:standard slot:11 autostart
import math
import time
import hub

color_sensor = hub.port.F.device  # F für FINNtastisch
color_sensor.mode((5, 1))
time.sleep(0.3)


cb = hub.button.center.callback()
hub.button.center.callback(lambda _: None)


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

hub.display.show(hub.Image("33333:33333:33333:33333:33333"))
hub.led(7)

buttons.pressed(hub.button.POWER)
hub.button.left.was_pressed()

while not buttons.pressed(hub.button.POWER):
    brightness, color, r, g, b = color_sensor.get()
    # print(brightness, color, r, g, b)
    _current_state = current_state(r, g, b)
    # print(_current_state)
    # time.sleep(1)
    if hub.button.left.was_pressed():
        counter = 0
        hub.display.show(hub.Image("33333:33333:33333:33333:33333"))
        hub.led(7)
    if last_state != _current_state and _current_state is not None:
        print("Laststate: ", last_state, "_current_state: ", _current_state)

        if last_state == ((_current_state - 1) % 3):
            counter += 1
            print("Plus 1")

        elif last_state == ((_current_state + 1) % 3):
            counter -= 1
            print("Minus 1")

        print(counter)
        last_state = _current_state

        lenght = counter / 5
        print(lenght)

        for x in range(5):
            hub.display.pixel(2, x, 100 if abs(round(lenght)) > x else 3)

        hub.led(6 if lenght > 0 else (9 if lenght < 0 else 7))





hub.display.show(hub.Image("33333:39393:33933:39393:33333"))
while not buttons.pressed(hub.button.POWER):
    ...
hub.button.center.callback(cb)


#TODO add real calculations not just approximations
# LEGO type:standard slot:4 autostart

import hub as hb
import time
from spike import PrimeHub
import random

hub = PrimeHub()

state_left = False
state_right = False
start = time.ticks_ms()  # type: ignore

field = [
    [False, False, False, False, False],
    [False, False, False, False, False],
    [False, False, False, False, False],
    [False, False, False, False, False],
    [False, False, False, False, False],
]
position = 2

lifes = 2

zeit = 1000


def show_field():
    for y, row in enumerate(field):
        for x, col in enumerate(row):
            if col:
                hub.light_matrix.set_pixel(x, y, 50)
            else:
                hub.light_matrix.set_pixel(x, y, 0)

    hub.light_matrix.set_pixel(position, 4)


def main():
    global lifes, position, start, zeit
    hub.right_button.was_pressed()
    hub.left_button.was_pressed()

    hub.light_matrix.set_pixel(2, 4)

    hub.status_light.on("green")

    while lifes > 0:
        if hub.right_button.was_pressed():
            if not position == 4:
                position = position + 1
                show_field()

        if hub.left_button.was_pressed():
            if not position == 0:
                position = position - 1
                show_field()

        if time.ticks_ms() > start + zeit:  # type: ignore
            last_row = field.pop()
            zeit = zeit -20
            if True in last_row:
                lifes = lifes - 1

            if lifes == 1:
                hub.status_light.on("yellow")

            field.insert(0, [False, False, False, False, False])
            field[0][random.randint(0, 4)] = True
            show_field()
            start = time.ticks_ms()  # type: ignore

        if field[4][position]:
            field[4][position] = False

    hub.status_light.on("red")

    while True:
        time.sleep(0.5)

        hub.light_matrix.off()


hb.display.show(hb.Image("00000:09090:00900:09990:900009"))

time.sleep(0.5)

hub.light_matrix.off()

hb.display.show(hb.Image("09090:00900:00000:00900:900009"))
       
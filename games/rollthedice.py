import random
import time
from spike import PrimeHub
import hub as hb

hub = PrimeHub()


sides = [
    hb.Image("00000:00000:00000:00000:00000"),
    hb.Image("00000:00000:00900:00000:00000"),
    hb.Image("90000:00000:00000:00000:00009"),
    hb.Image("90000:00000:00900:00000:00009"),
    hb.Image("90009:00000:00000:00000:90009"),
    hb.Image("90009:00000:00900:00000:90009"),
    hb.Image("90009:00000:90009:00000:90009"),
    hb.Image("09090:00000:90909:00000:09090"),
    hb.Image("90909:00000:90009:00000:90909"),
]


def main():
    hub.right_button.was_pressed()
    hb.button.center.was_pressed()

    m = 6
    hub.light_matrix.show_image("ARROW_S")
    while not hb.button.center.was_pressed():
        if hub.left_button.was_pressed():
            hb.display.show(hb.Image("00900:99999:99999:99999:09990"))
            time.sleep(0.5)
            hub.light_matrix.write("Das ist eine von 8 Melonen.")  # 🍒
            time.sleep(0.25)
            hb.display.show(hb.Image("00900:99999:99999:99999:09990"))
            m = 8

    while True:
        side = random.randint(1, m)
        hb.display.show(sides[side])
        while not hb.button.center.was_pressed():
            if hub.right_button.was_pressed():
                return

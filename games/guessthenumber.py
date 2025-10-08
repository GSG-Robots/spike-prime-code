# LEGO type:standard slot:5 autostart

import time
import hub as hb
from spike import PrimeHub
import random
hub = PrimeHub()
numbers = [
    hb.Image("09990:09090:09090:09090:09990"),
    hb.Image("00900:09900:00900:00900:09990"),
    hb.Image("09990:00090:09990:09000:09990"),
    hb.Image("09990:00090:09990:00090:09990"),
    hb.Image("09090:09090:09990:00090:00090"),
    hb.Image("09990:09000:09990:00090:09990"),
    hb.Image("09990:09000:09990:09090:09990"),
    hb.Image("09990:00090:00900:09000:09000"),
    hb.Image("09990:09090:09990:09090:09990"),
    hb.Image("09990:09090:09990:00090:09990"),
    hb.Image("90999:90909:90909:90909:90999"),
    hb.Image("90090:90990:90090:90090:90999"),
    hb.Image("90999:90009:90999:90900:90999"),
    hb.Image("90999:90009:90999:90009:90999"),
    hb.Image("90909:90909:90999:90009:90009"),
    hb.Image("90999:90900:90999:90009:90999"),
    hb.Image("90999:90900:90999:90909:90999"),
    hb.Image("90999:90009:90090:90900:90900"),
    hb.Image("90999:90909:90999:90909:90999"),
    hb.Image("90999:90909:90999:90009:90999"),
]

def main():
    guess = 0
    numbertoguess = random.randint(0, 19)
    hb.display.show(numbers[guess])
    hub.left_button.was_pressed()
    hub.right_button.was_pressed()
    hb.button.center.was_pressed()
    while not (hb.button.left.is_pressed() and hb.button.right.is_pressed()):
        if hub.right_button.was_pressed():
            guess += 1
            if guess == 20:
                guess = 19
            hb.display.show(numbers[guess])

        if hub.left_button.was_pressed():
            guess -= 1
            if guess == -1:
                guess = 0
            hb.display.show(numbers[guess])
        if hb.button.center.was_pressed():
            if guess == numbertoguess:
                hub.light_matrix.show_image("HAPPY")
                time.sleep(1)
                break
            if guess > numbertoguess:
                hub.light_matrix.show_image("ARROW_W")
                time.sleep(1)
                hb.display.show(numbers[guess])
            if guess < numbertoguess:
                hub.light_matrix.show_image("ARROW_E")
                time.sleep(1)
                hb.display.show(numbers[guess])



    
    
# LEGO type:standard slot:19 autostart
import random
import time

import hub
from spike import PrimeHub

brick = PrimeHub()

number = 0

brick.light_matrix.write(number)
brick.right_button.was_pressed()
brick.left_button.was_pressed()
while True:
    if brick.right_button.was_pressed():
        number += 1
        if number == 10:
            number = 9
        brick.light_matrix.write(number)
    if brick.left_button.was_pressed():
        number -= 1
        if number == -1:
            number = 0
        brick.light_matrix.write(number)
        

            

    
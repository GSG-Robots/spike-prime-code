# LEGO type:standard slot:19 autostart
import hub
import time
from spike import PrimeHub
import random
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
        

            

    
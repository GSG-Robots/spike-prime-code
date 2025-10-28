# LEGO type:standard slot:18 autostart


import random
import time

from spike import PrimeHub, control

brick = PrimeHub()

place = [0, 2, 4]
while True:
    try:
        brick.light_matrix.show_image("ARROW_S")
        while True:
            if brick.left_button.was_pressed():
                raise SystemExit
    except KeyboardInterrupt:
        brick.light_matrix.off()
        control.wait_for_seconds(random.randint(0, 5))
        brick.light_matrix.off()
        rand = random.choice(place)
        brick.light_matrix.set_pixel(rand, 4, 100)
        started = time.time()
        selected = 17
        try:
            while True:
                if brick.left_button.was_pressed():
                    selected = 0
                    break
                elif brick.right_button.was_pressed():
                    selected = 4
                    break
        except KeyboardInterrupt:
            selected = 2
        # brick.light_matrix.off()
        if rand == selected:
            brick.light_matrix.write(round((time.time() - started)))
        else:
            brick.light_matrix.show_image("SAD")
        try:
            while True:
                control.wait_for_seconds(0.1)
        except KeyboardInterrupt:
            brick.light_matrix.off()

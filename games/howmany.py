# LEGO type:standard slot:17 autostart


import random
from spike import PrimeHub
import hub as hb
import time
brick = PrimeHub()

def main():
    def numtodisplay(number):
        # brick.light_matrix.off()
        if not 0 <= number <= 25:
            raise ValueError
        # lines = (number // 5) - 1
        # extra = number % 5
        # for x in range(lines):
        #     for y in range(4):
        #         brick.light_matrix.set_pixel(x, y, 100)
        # for x in range(extra):
        #     brick.light_matrix.set_pixel(lines + 1, x, 100)
            
        
        for x in range(5):
            for y in range(5):
                if number > 0:
                    number -= 1
                    brick.light_matrix.set_pixel(y, x, 100)
                else:
                    brick.light_matrix.set_pixel(y, x, 0)

    try:
        while True:
            brick.light_matrix.show_image("ARROW_S")
            hb.button.center.was_pressed()
            while not hb.button.center.was_pressed():
                if brick.left_button.was_pressed():
                    raise SystemExit
            brick.light_matrix.off()
            time.sleep(random.randint(0, 5))
            brick.light_matrix.off()
            howmany = random.randint(5, 25)
            before = []
            for x in range(howmany):
                while True:
                    randx = random.randint(0, 4)
                    randy = random.randint(0, 4)
                    if [randx, randy] not in before:
                        brick.light_matrix.set_pixel(randx, randy, 100)
                        before.append([randx, randy])
                        break
            time.sleep(3)
            selected = 0
            brick.light_matrix.off()
            while not hb.button.center.was_pressed():
                if brick.left_button.was_pressed():
                    selected -= 1
                elif brick.right_button.was_pressed():
                    selected += 1
                if selected > 25:
                    selected = 25
                elif selected < 0:
                    selected = 0
                numtodisplay(selected)
                time.sleep(.1)
                # brick.light_matrix.write(selected)
                # print(selected)
            # brick.light_matrix.off()
            if selected == howmany:
                brick.light_matrix.show_image("HAPPY")
            else:
                brick.light_matrix.show_image("SAD")
            while not hb.button.center.was_pressed():
                time.sleep(0.1)
            brick.light_matrix.off()
    except SystemExit:
        return

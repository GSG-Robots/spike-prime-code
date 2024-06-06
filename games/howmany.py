# LEGO type:standard slot:17 autostart


import random
from spike import PrimeHub, control

brick = PrimeHub()


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
        control.wait_for_seconds(3)
        selected = 0
        brick.light_matrix.off()
        try:
            while True:
                if brick.left_button.was_pressed():
                    selected -= 1
                elif brick.right_button.was_pressed():
                    selected += 1
                if selected > 25:
                    selected = 25
                elif selected < 0:
                    selected = 0
                numtodisplay(selected)
                control.wait_for_seconds(.1)
                # brick.light_matrix.write(selected)
                # print(selected)
        except KeyboardInterrupt:
            # brick.light_matrix.off()
            if selected == howmany:
                brick.light_matrix.show_image("HAPPY")
            else:
                brick.light_matrix.show_image("SAD")
            try:
                while True:
                    control.wait_for_seconds(0.1)
            except KeyboardInterrupt:
                brick.light_matrix.off()

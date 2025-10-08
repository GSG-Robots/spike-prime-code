
import time
import hub as hb
import random
from spike import PrimeHub

hub = PrimeHub()

def main():
    position_player = 2
    last_millis = time.ticks_ms()   # type: ignore
    speed = 500
    field = [
        (False, False, False, False, False),
        (False, False, False, False, False),
        (False, False, False, False, False),
        (False, False, False, False, False),
        (False, False, False, False, False),
    ]
    gjh = False
    hb.button.center.was_pressed()
    while not hb.button.center.was_pressed():
        if hub.left_button.was_pressed():
            if position_player > 0:
                hub.light_matrix.set_pixel(position_player, 4, 0)
                position_player -= 1

        if hub.right_button.was_pressed():
            if position_player < 4:
                hub.light_matrix.set_pixel(position_player, 4, 0)
                position_player += 1

        hub.light_matrix.set_pixel(position_player, 4)

        if field[4][position_player]:
            break

        print(time.ticks_ms() - last_millis, speed) # type: ignore
        if not gjh and time.ticks_ms() - last_millis > speed:   # type: ignore
            gjh = True
            field.pop()

            new_line = [False, False, False, False, False]

            new_line[random.randint(0, 4)] = True
            # new_line [random.randint(0, 4)] = True
            # new_line [random.randint(0, 4)] = True
            a = tuple(new_line)
            assert len(a) == 5
            field.insert(0, a)   

            for y, line in enumerate(field):
                for x, value in enumerate(line):
                    hub.light_matrix.set_pixel(x, y, 70 if value else 0)

        if gjh and time.ticks_ms() - last_millis > speed * 2:   # type: ignore
            last_millis = time.ticks_ms()   # type: ignore
            gjh = False
            field.pop()
            field.insert(0, (False, False, False, False, False))
            for y, line in enumerate(field):
                for x, value in enumerate(line):
                    hub.light_matrix.set_pixel(x, y, 70 if value else 0)

    hub.light_matrix.show_image("SAD")

# LEGO type:standard slot:10 autostart

from spike import PrimeHub, control
import random
from hub import led

brick = PrimeHub()


def draw_memory(images: list):
    images.insert(12, None)
    for x in range(5):
        for y in range(5):
            brick.light_matrix.set_pixel(
                x,
                y,
                (
                    100
                    if images[y + x * 5] is True
                    else (0 if images[y + x * 5] is None else 80)
                ),
            )


def select_card(images, last_index=None):
    images = images[::1]
    if last_index is not None:
        images[last_index] = None
    selected = 0
    while images[selected] is None:
        selected += 1
    print(images, images, selected)
    i = images[::1]
    i[selected] = True
    draw_memory(i)
    try:
        while True:
            prev_select = selected
            if brick.left_button.was_pressed():
                selected -= 1
                if selected < 0:
                    selected = prev_select
                while images[selected] is None:
                    selected -= 1
                    if selected < 0:
                        selected = prev_select
            if brick.right_button.was_pressed():
                selected += 1
                if selected >= len(images):
                    selected = prev_select
                while images[selected] is None:
                    selected += 1
                    if selected >= len(images):
                        selected = prev_select
            if selected < 0:
                selected = 0
            if selected >= len(images):
                selected = len(images) - 1

            if selected != prev_select:
                i = images[::1]
                i[selected] = True
                draw_memory(i)
    except KeyboardInterrupt:
        try:
            brick.light_matrix.show_image(images[selected])
            while True:
                ...
        except KeyboardInterrupt:
            return selected


def main():
    current_player = True
    score_red = 0
    score_blue = 0
    images = [
        "ANGRY",
        "SWORD",
        "BUTTERFLY",
        "GHOST",
        "TARGET",
        "TSHIRT",
        "SNAKE",
        "HEART",
        "SKULL",
        "HAPPY",
        "DUCK",
        "GIRAFFE",
    ] * 2
    # images = sorted(images, key=lambda x: random.random())
    print(1)
    while images.count(None) != len(images):
        print(2)
        led(9 if current_player else 3)

        first = select_card(images)
        second = select_card(images, first)
        if images[first] == images[second]:
            images[first] = None
            images[second] = None
            led(6)
            control.wait_for_seconds(1.5)
            led(9 if current_player else 3)
            if current_player:
                score_red += 1
            else:
                score_blue += 1
        else:
            current_player = not current_player

    try:
        draw_memory(images)
        while True:
            if score_red == score_blue:
                led(6)
            elif score_red > score_blue:
                led(9)
            else:
                led(3)
            control.wait_for_seconds(0.1)
            led(0)
            control.wait_for_seconds(0.1)
    except KeyboardInterrupt:
        raise SystemExit


main()

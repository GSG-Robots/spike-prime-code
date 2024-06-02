# LEGO type:standard slot:16 autostart


import random
import time
import copy
from spike import PrimeHub, control

brick = PrimeHub()

I = True
O = False


image_dic = {
"full":     [[0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0], [0, 0, 0, 0, 0]],
"blanc":    [[100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100]],
"happy":    [[0, 0, 0, 0, 0], [0, 100, 0, 100, 0], [0, 0, 0, 0, 0], [100, 0, 0, 0, 100], [0, 100, 100, 100, 0]],
"sad":      [[0, 0, 0, 0, 0], [0, 100, 0, 100, 0], [0, 0, 0, 0, 0], [0, 100, 100, 100, 0], [100, 0, 0, 0, 100]],
"heart":    [[0, 100, 0, 100, 0], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [0, 100, 100, 100, 0], [0, 0, 100, 0, 0]],
"home":     [[0, 0, 100, 0, 0], [0, 100, 100, 100, 0], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100]],
"flower":   [[0, 0, 100, 0, 0], [0, 100, 0, 100, 0], [0, 0, 100, 0, 0], [0, 100, 100, 0, 0], [0, 0, 100, 0, 0]],
"arrow_up":             [[0, 0, 100, 0, 0], [0, 100, 100, 100, 0], [100, 0, 100, 0, 100], [0, 0, 100, 0, 0], [0, 0, 100, 0, 0]],
"arrow_down":           [[0, 0, 100, 0, 0], [0, 0, 100, 0, 0], [100, 0, 100, 0, 100], [0, 100, 100, 100, 0], [0, 0, 100, 0, 0]],
"arrow_right":          [[0, 0, 100, 0, 0], [0, 0, 0, 100, 0], [100, 100, 100, 100, 100], [0, 0, 0, 100, 0], [0, 0, 100, 0, 0]],
"arrow_left":           [[0, 0, 100, 0, 0], [0, 100, 0, 0, 0], [100, 100, 100, 100, 100], [0, 100, 0, 0, 0], [0, 0, 100, 0, 0]],
"square":               [[100, 100, 100, 100, 100], [100, 0, 0, 0, 100], [100, 0, 0, 0, 100], [100, 0, 0, 0, 100], [100, 100, 100, 100, 100]],
"middle_square":        [[0, 0, 0, 0, 0], [0, 100, 100, 100, 0], [0, 100, 0, 100, 0], [0, 100, 100, 100, 0], [0, 0, 0, 0, 0]],             
"square_filled":        [[100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100], [100, 100, 100, 100, 100]],
"middle_square_filled": [[0, 0, 0, 0, 0], [0, 100, 100, 100, 0], [0, 100, 100, 100, 0], [0, 100, 100, 100, 0], [0, 0, 0, 0, 0]], 
"fish":     [[0, 0, 0, 0, 0], [0, 100, 100, 0, 100], [100, 100, 100, 100, 100], [0, 100, 100, 0, 100], [0, 0, 0, 0, 0]],
"diamond":  [[0, 0, 0, 0, 0], [0, 100, 100, 100, 0], [100, 90, 90, 90, 100], [0, 100, 90, 100, 0], [0, 0, 100, 0, 0]], 
"key":      [[0, 0, 0, 0, 0], [0, 100, 0, 0, 0], [100, 0, 100, 100, 100], [0, 100, 0, 0, 100], [0, 0, 0, 0, 0]]
}
def image(image):
    global image_dic
    return copy.deepcopy(image_dic[image])

def animations(image_list):
    try:
        while True:
            for x in image_list:
                draw(x)
                wait_for_second(.5)
    except KeyboardInterrupt:
        draw(image("blanc"))




def draw(image):
    for y, row in enumerate(image):
        for x, column in enumerate(row):
            if column is False:
                column = 0
            if column is True:
                column = 100
            brick.light_matrix.set_pixel(x, y, column)


def lownumber(number):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 25:
        raise ValueError("Number must be between 0 and 25")
    return [
        [
            I
            if number > x + y * 5
            else O
            for x in range(0, 5)
        ]
        for y in range(0, 5)
    ]


def highnumber(number):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 599:
        raise ValueError("Number must be between 0 and 599")
    a, b, c = tuple(int(x) for x in ("00"+str(number))[-3:])
    image = [
        [I if c > x else O for x in range(5)],
        [I if c > x else O for x in range(5, 10)],
        [90 if b > x else O for x in range(5)],
        [90 if b > x else O for x in range(5, 10)],
        [I if a > x else O for x in range(5)],
    ]
    return list(zip(*image[::-1]))


def shownumber(number):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if number < 0:
        raise ValueError("Number must not be below 0")
    elif number <= 9:
        brick.light_matrix.write(number)
    elif number <= 25:
        draw(lownumber(number))
    elif number <= 599:
        draw(highnumber(number))
    else:
        raise ValueError("Number must be below or equal to 599")

def move(lis, direction="up", step=0):
    if direction == "up":
        for x in range(step):
            del lis[0]
            lis.append([0, 0, 0, 0, 0])
    elif direction == "down":
        for x in range(step):
            del lis[4]
            lis.insert(0, [0, 0, 0, 0, 0])
    elif direction == "right":
        print(lis)
        lis = list(zip(*lis[::1]))
        for x in range(step):
            del lis[0]
            lis.append([0, 0, 0, 0, 0])
        lis = list(zip(*lis[::-1])) 
    elif direction == "left":
        lis = list(zip(*lis[::-1]))
        for x in range(step):
            del lis[0]
            lis.append([0, 0, 0, 0, 0]) 
        lis = list(zip(*lis[::1]))
    return lis
    
def move_animations(image, direction):
    for y in range(100):
        for x in (4):
            draw(move(image), direction, 1)
            time.sleep(.5)
#i can't test it

selected = 0
while True:
    if brick.left_button.was_pressed():
        selected -= 1
    elif brick.right_button.was_pressed():
        selected += 1
    if selected > 599:
        selected = 599
    elif selected < 0:
        selected = 0
    shownumber(selected)
    control.wait_for_seconds(0.1)

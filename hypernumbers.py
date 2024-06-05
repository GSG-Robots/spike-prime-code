# LEGO type:standard slot:16 autostart


import random
import time

# import copy
from spike import PrimeHub, control

brick = PrimeHub()

I = True
O = False


brightnesses = [0, 20, 40, 50, 60, 75, 90, 100]

image_dic = {
    "blank": [
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
        [0, 0, 0, 0, 0],
    ],
    "full": [
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
    ],
    "happy": [
        [0, 0, 0, 0, 0],
        [0, 100, 0, 100, 0],
        [0, 0, 0, 0, 0],
        [100, 0, 0, 0, 100],
        [0, 100, 100, 100, 0],
    ],
    "sad": [
        [0, 0, 0, 0, 0],
        [0, 100, 0, 100, 0],
        [0, 0, 0, 0, 0],
        [0, 100, 100, 100, 0],
        [100, 0, 0, 0, 100],
    ],
    "heart": [
        [0, 100, 0, 100, 0],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [0, 100, 100, 100, 0],
        [0, 0, 100, 0, 0],
    ],
    "home": [
        [0, 0, 100, 0, 0],
        [0, 100, 100, 100, 0],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
    ],
    "flower": [
        [0, 0, 100, 0, 0],
        [0, 100, 0, 100, 0],
        [0, 0, 100, 0, 0],
        [0, 100, 100, 0, 0],
        [0, 0, 100, 0, 0],
    ],
    "arrow_up": [
        [0, 0, 100, 0, 0],
        [0, 100, 100, 100, 0],
        [100, 0, 100, 0, 100],
        [0, 0, 100, 0, 0],
        [0, 0, 100, 0, 0],
    ],
    "arrow_down": [
        [0, 0, 100, 0, 0],
        [0, 0, 100, 0, 0],
        [100, 0, 100, 0, 100],
        [0, 100, 100, 100, 0],
        [0, 0, 100, 0, 0],
    ],
    "arrow_right": [
        [0, 0, 100, 0, 0],
        [0, 0, 0, 100, 0],
        [100, 100, 100, 100, 100],
        [0, 0, 0, 100, 0],
        [0, 0, 100, 0, 0],
    ],
    "arrow_left": [
        [0, 0, 100, 0, 0],
        [0, 100, 0, 0, 0],
        [100, 100, 100, 100, 100],
        [0, 100, 0, 0, 0],
        [0, 0, 100, 0, 0],
    ],
    "square": [
        [100, 100, 100, 100, 100],
        [100, 0, 0, 0, 100],
        [100, 0, 0, 0, 100],
        [100, 0, 0, 0, 100],
        [100, 100, 100, 100, 100],
    ],
    "middle_square": [
        [0, 0, 0, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 0, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 0, 0],
    ],
    "square_filled": [
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
        [100, 100, 100, 100, 100],
    ],
    "middle_square_filled": [
        [0, 0, 0, 0, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 100, 100, 100, 0],
        [0, 0, 0, 0, 0],
    ],
    "fish": [
        [0, 0, 0, 0, 0],
        [0, 100, 100, 0, 100],
        [100, 100, 100, 100, 100],
        [0, 100, 100, 0, 100],
        [0, 0, 0, 0, 0],
    ],
    "diamond": [
        [0,    0,   0,   0,   0],
        [0,  100, 100, 100,   0],
        [100, 90,  90,  90, 100],
        [0,  100,  90, 100,   0],
        [0,    0, 100,   0,   0],
    ],
    "key": [
        [0, 0, 0, 0, 0],
        [0, 100, 0, 0, 0],
        [100, 0, 100, 100, 100],
        [0, 100, 0, 0, 100],
        [0, 0, 0, 0, 0],
    ],
}


def image(image) -> list[list[str]]:
    global image_dic
    return [[int(float(y)) for y in x] for x in image_dic[image]]

def numtopix(number: int = 0):
    pix_lis = image("blank")
    number -= 1
    if number != -1:
        pix_lis[number // 5][number % 5] = 100
    return pix_lis

def numtopix_b(number: int = 0):
    return (0b111 << ((number - 1) * 3)) if number else 0b0


def animations(image_list):
    try:
        while True:
            for x in image_list:
                draw(x)
                control.wait_for_seconds(0.5)
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

def draw_bin(number: int):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 37778931862957161709567:
        raise ValueError("Number must be between 0 and 37778931862957161709567")
    
    for z in range(25):
        x = 4 - z // 5
        y = 4 - z % 5
        # print(x, y, brightnesses[number & 7])
        brick.light_matrix.set_pixel(y, x, brightnesses[number & 7])
        number >>= 3
        # brick.light_matrix.set_pixel(4, 4, 100)

def b2l(number: int):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 33554431:
        raise ValueError("Number must be between 0 and 33554431")
    number <<= 1
    counter = -1
    result = [
        [False, False, False, False, False],
        [False, False, False, False, False],
        [False, False, False, False, False],
        [False, False, False, False, False],
        [False, False, False, False, False],
    ]
    
    while number != 0 and counter < 25 - 1:
        result[4 - (counter := counter + 1) // 5][4 - counter % 5] = bool((number := (number >> 1)) % 2)
    return result


def l2n(list_):
    r = 0
    for row in list_:
        for column in row:
            print(brightnesses.index(column))
            r += brightnesses.index(column if column in brightnesses else 50) 
            r <<= 3
    return r >> 3


def lownumber(number: int = 0, brightness: int = None):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 25:
        raise ValueError("Number must be between 0 and 25")
    if brightness is None:
        brightness = 100
    return [
        [brightness if number > x + y * 5 else O for x in range(0, 5)]
        for y in range(0, 5)
    ]


def highnumber(
    number: int = 0, brightness: int = None, brightness_kontrast: int = None
):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 599:
        raise ValueError("Number must be between 0 and 599")
    if brightness is None:
        brightness = 100
    if brightness_kontrast is None:
        brightness_kontrast = 90
    a, b, c = tuple(int(x) for x in ("00" + str(number))[-3:])
    image = [
        [brightness if c > x else O for x in range(5)],
        [brightness if c > x else O for x in range(5, 10)],
        [brightness_kontrast if b > x else O for x in range(5)],
        [brightness_kontrast if b > x else O for x in range(5, 10)],
        [brightness if a > x else O for x in range(5)],
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


# def numtopixel(number):
#     brightness = 100
#     if not isinstance(number, int):
#         raise TypeError("Number must be int")
#     if not 0 <= number <= 25:
#         raise ValueError("Number must be between 0 and 25")
#     if brightness is None:
#         brightness = 100
#     # return [
#     #     [
#     #         brightness
#     #         if (x+1)*(y+1) == number
#     #         else O
#     #         for x in range(0, 5)
#     #     ]
#     #     for y in range(0, 5)
#     # ]
#     before = 0
#     ylist = []
#     for y in range(0, 5):
#         xlist = []
#         for x in range(0, 5):
#             print("x", x)
#             print("y", y)
#             if (x + 1) + ((y + 1) * 5) == number and before != 1:
#                 xlist.append(brightness)
#                 before = 1
#             else:
#                 xlist.append(0)
#         print("xlist", xlist)
#         ylist.append(xlist)
#     print("ylist", ylist)
#     return ylist
#     # pixel = []
#     # lines = (number // 5) - 1
#     # extra = number % 5
#     # x = 0
#     # while x > lines:
#     #     pixel.append([brightness, brightness, brightness, brightness, brightness])
#     #     x += 1
#     # pixel.append([brightness for x in range(5-extra)])


selected = 10


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
    dec_oppposite = {
        "up": "down",
        "down": "up",
        "right": "left",
        "left": "right"
    }
    for y in range(100):
        for x in range(4):
            draw(move(image, direction, 1))
            time.sleep(0.5)
        for z in range(4):
            draw(move(image, dec_oppposite[direction], 1))
            time.sleep(0.5)
                

# i can't test it
def dra(image):
    for x in enumerate(image):
        brick.light_matrix.set_pixel(x // 5, x % 5, image[x])
test = [0, 100, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]

dra(test)
# selected = 0
# while True:
#     if brick.left_button.was_pressed():
#         selected -= 1
#     elif brick.right_button.was_pressed():
#         selected += 1
#     if selected > 25:
#         selected = 25
#     elif selected < 0:
#         selected = 0
#     print(selected)
#     # draw(numtopix(selected))
#     draw_bin(numtopix_b(selected))

#     control.wait_for_seconds(0.1)

# print(image("happy"))
# print(l2n(image("happy")))
# print(draw_bin(l2n(image("happy"))))
# while True:
#     img = 328238
#     for x in range(6):
#         draw(draw_bin(img))
#         img = (img << 5) & 33554431
#         time.sleep(0.5)
#     img = 328238
#     for x in range(6):
#         draw(draw_bin(img))
#         img = (img >> 5) & 33554431
#         time.sleep(0.5)

print(l2n(image("diamond")))
# img = 4713143110832790437888
# for x in range(6):
#     a = (img << 15 * x) & 37778931862957161709567 # 0b00000000000000000000000001111111111111111111111111
#     b = ((img << 15 * x)) >> 75 # 0b11111111111111111111111110000000000000000000000000
#     print(a)
#     draw_bin(a)
#     time.sleep(.5)
#     draw_bin(b)
#     time.sleep(.5)

draw_bin(143868269464125888)

# move_animations(image("happy"), "up")

# move_animations(image("happy"), "up")


# for x in [0, 20, 40, 50, 60, 75, 90, 100]:
#     draw([[x]*5]*5)
#     time.sleep(0.3)
    

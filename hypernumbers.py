# LEGO type:standard slot:16 autostart


from spike import PrimeHub, control

brick = PrimeHub()

I = True
O = False


def draw(image):
    for y, row in enumerate(image):
        for x, column in enumerate(row):
            if column is False:
                column = 0
            if column is True:
                column = 100
            brick.light_matrix.set_pixel(x, y, column)


def lownumber(number: int = 0, brightness: int = None):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 25:
        raise ValueError("Number must be between 0 and 25")
    if brightness is None:
        brightness = 100
    return [
        [
            brightness
            if number > x + y * 5
            else O
            for x in range(0, 5)
        ]
        for y in range(0, 5)
    ]


def highnumber(number: int = 0, brightness: int = None, brightness_kontrast: int = None):
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 599:
        raise ValueError("Number must be between 0 and 599")
    if brightness is None:
        brightness = 100
    if brightness_kontrast is None:
        brightness_kontrast = 90
    a, b, c = tuple(int(x) for x in ("00"+str(number))[-3:])
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

def numtopixel(number):
    brightness = 100
    if not isinstance(number, int):
        raise TypeError("Number must be int")
    if not 0 <= number <= 25:
        raise ValueError("Number must be between 0 and 25")
    if brightness is None:
        brightness = 100
    # return [
    #     [    
    #         brightness
    #         if (x+1)*(y+1) == number
    #         else O
    #         for x in range(0, 5)
    #     ]
    #     for y in range(0, 5)
    # ]
    before = 0
    ylist = []
    for y in range(0, 5):
        xlist = []
        for x in range(0, 5):
            print("x", x)
            print("y", y)
            if (x+1) + ((y+1) * 5) == number and before != 1:
                xlist.append(brightness)
                before = 1
            else:
                xlist.append(0)
        print("xlist", xlist)
        ylist.append(xlist)
    print("ylist", ylist)
    return ylist
    # pixel = []
    # lines = (number // 5) - 1
    # extra = number % 5
    # x = 0
    # while x > lines:
    #     pixel.append([brightness, brightness, brightness, brightness, brightness])
    #     x += 1
    # pixel.append([brightness for x in range(5-extra)])
    
selected = 10
while True:
    if brick.left_button.was_pressed():
        selected -= 1
    elif brick.right_button.was_pressed():
        selected += 1
    if selected > 25:
        selected = 25
    elif selected < 0:
        selected = 0
    draw(numtopixel(selected))

    control.wait_for_seconds(0.1)

# LEGO type:standard slot:15 autostart

from spike import PrimeHub, control

brick = PrimeHub()


def numtopix(number, brightness):
    pix_lis = pitch
    number -= 1
    if number != -1:
        pix_lis[number // 5][number % 5] = brightness
    return pix_lis


def draw(image):
    for y, row in enumerate(image):
        for x, column in enumerate(row):
            if column is False:
                column = 0
            if column is True:
                column = 100
            brick.light_matrix.set_pixel(x, y, column)

def dra(image):
    for x in image:
        brick.light_matrix.set_pixel(x // 5, x % 5, x)

selected_lis = [1, 3, 5, 11, 13, 15, 21, 23, 25]
current_player = True
pitch = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
winner = 0
while True:
    try:
        selected = 0
        while True:
            
            if brick.left_button.was_pressed():
                selected -= 1
            elif brick.right_button.was_pressed():
                selected += 1
            if selected > 9:
                selected = 9
            elif selected < 0:
                selected = 0
    except KeyboardInterrupt:
        print(selected)
        # draw(numtopix(selected))
        draw(numtopix(selected_lis[selected], 90 if current_player else 100))
        selected_lis.pop(selected)
        control.wait_for_seconds(0.1)
        current_player = not current_player
        for x in range(3):
            if pitch[x].count(90) == 3:
                winner = 1
            if pitch[x].count(80) == 3:
                winner = 2
                
        pitch = list(zip(*pitch[::1]))
        
        for x in range(3):
            if pitch[x].count(90) == 3:
                winner = 1
            if pitch[x].count(80) == 3:
                winner = 2
                
        pitch = list(zip(*pitch[::-1])) 
        
        if pitch[0] == pitch[12] == pitch[24] == 100 or pitch[4] == pitch[12] == pitch[20] == 90:
            winner = 1
        if pitch[0] == pitch[12] == pitch[24] == 90 or pitch[4] == pitch[12] == pitch[20] == 80:
            winner = 2
        if winner != 0:
            try:
                brick.light_matrix.write(winner)
            except KeyboardInterrupt:
                break
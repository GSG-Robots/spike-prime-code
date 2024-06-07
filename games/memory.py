# LEGO type:standard slot:2 autostart

from spike import PrimeHub, control
import random
from hub import led

brick = PrimeHub()

def draw_memory(free_positions_: list):
    free_positions_.insert(13, True) 
    for x in range(5):
        for y in range(5):
            brick.light_matrix.set_pixel(x, y, 100 if free_positions_[y][x*5] else 0)


            

free_positions = [True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True, True]
current_player = True
selected = 0
images = ["ANGRY", "SWORD", "BUTTERFLY", "GHOST", "TARGET", "TSHIRT", "SNAKE", "HEART", "SKULL", "HAPPY", "DUCK", "GIRAFFE"]
random.shuffle(images)
while True:
    led(9 if current_player else 3)
    try:
        while True:
            if brick.left_button.was_pressed():
                selected -= 1
            if brick.right_button.was_pressed():
                selected += 1
            if selected < 0:
                selected = 0
            if selected > len(free_positions):
                selected = len(free_positions) 
    except KeyboardInterrupt:
        
        
        current_player = not current_player
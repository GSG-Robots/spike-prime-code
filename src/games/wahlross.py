# LEGO type:standard slot:4 autostart


from spike import PrimeHub

hub = PrimeHub()

state_left = False
state_right = False

hub.right_button.was_pressed()
hub.left_button.was_pressed()

while True:
    if hub.left_button.was_pressed():
        state_left= not state_left
        if state_left:
            hub.light_matrix.set_pixel(0, 4)
        else:
            hub.light_matrix.set_pixel(0, 4, 0)

    if hub.right_button.was_pressed():
        state_right= not state_right
        if state_right:
            hub.light_matrix.set_pixel(4, 4)
        else:
            hub.light_matrix.set_pixel(4, 4, 0)
            
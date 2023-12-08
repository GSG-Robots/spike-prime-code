# LEGO type:standard slot:8 autostart
"""Short run to show battery show"""

import time
import hub  # type: ignore # pylint: disable=import-error
import spike

hb = spike.PrimeHub()

hb.light_matrix.set_pixel(0, 0, 50)
hb.light_matrix.set_pixel(4, 0, 50)
hb.light_matrix.set_pixel(0, 4, 50)
hb.light_matrix.set_pixel(4, 4, 50)


while True:
    try:
        height = round(hub.battery.capacity_left() / 10)

        delay = .1 if hub.battery.charger_detect() is not False else 0

        if height >= 0:
            hb.light_matrix.set_pixel(2, 0, 0)
        time.sleep(delay)
        if height >= 1:
            hb.light_matrix.set_pixel(2, 0, 75)
        time.sleep(delay)
        if height >= 2:
            hb.light_matrix.set_pixel(2, 0, 100)
        time.sleep(delay)
        if height >= 3:
            hb.light_matrix.set_pixel(2, 1, 75)
        time.sleep(delay)
        if height >= 4:
            hb.light_matrix.set_pixel(2, 1, 100)
        time.sleep(delay)
        if height >= 5:
            hb.light_matrix.set_pixel(2, 2, 75)
        time.sleep(delay)
        if height >= 6:
            hb.light_matrix.set_pixel(2, 2, 100)
        time.sleep(delay)
        if height >= 7:
            hb.light_matrix.set_pixel(2, 3, 75)
        time.sleep(delay)
        if height >= 8:
            hb.light_matrix.set_pixel(2, 3, 100)
        time.sleep(delay)
        if height >= 9:
            hb.light_matrix.set_pixel(2, 4, 75)
        time.sleep(delay)
        if height >= 10:
            hb.light_matrix.set_pixel(2, 4, 100)
            
        time.sleep(1)
        
        if hb.left_button.was_pressed():
            hb.light_matrix.set_pixel(1, 4, 100)
            hb.light_matrix.set_pixel(3, 4, 100)
            
        if hb.right_button.was_pressed():
            hb.light_matrix.set_pixel(1, 4, 0)
            hb.light_matrix.set_pixel(3, 4, 0)
    except SystemExit:
        break
    except KeyboardInterrupt:
        break
raise SystemExit

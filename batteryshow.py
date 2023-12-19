# LEGO type:standard slot:8 autostart
"""Short run to show battery show"""

import time
import hub  # type: ignore # pylint: disable=import-error
import spike

hb = spike.PrimeHub()
went_on_80 = -1

for x in ["A", "B", "C", "D", "E", "F"]:
    try:
        spike.ColorSensor(x).light_up_all(0)
    except RuntimeError:
        pass

hb.light_matrix.set_pixel(0, 0, 50)
hb.light_matrix.set_pixel(4, 0, 50)
hb.light_matrix.set_pixel(0, 4, 50)
hb.light_matrix.set_pixel(4, 4, 50)

brightness_multiplier = 2


def brightness(n):
    m = 1 if brightness_multiplier > 1 else brightness_multiplier
    return round(n*m)


while True:
    try:
        brightness_multiplier -= 0.2
        if brightness_multiplier < 0:
            brightness_multiplier = 0
        
        cap = hub.battery.capacity_left()
        height = round(cap / 10)
        if cap >= 80:
            if went_on_80 == -1:
                went_on_80 = time.time()
        else:
            went_on_80 = -1
        if went_on_80 != -1 and time.time() - went_on_80 > 60*10:
            brightness_multiplier = 1
            hb.light_matrix.set_pixel(0, 0, brightness(100))
            hb.light_matrix.set_pixel(4, 0, brightness(100))
            hb.light_matrix.set_pixel(0, 4, brightness(100))
            hb.light_matrix.set_pixel(4, 4, brightness(100))
            hb.speaker.beep(70, 0.2)
            time.sleep(0.1)
            hb.speaker.beep(65, 0.3)
            hb.light_matrix.set_pixel(0, 0, brightness(50))
            hb.light_matrix.set_pixel(4, 0, brightness(50))
            hb.light_matrix.set_pixel(0, 4, brightness(50))
            hb.light_matrix.set_pixel(4, 4, brightness(50))

        delay = 0.1 if hub.battery.charger_detect() is not False else 0

        if height >= 0:
            hb.light_matrix.set_pixel(2, 0, brightness(0))
        time.sleep(delay)
        if height >= 1:
            hb.light_matrix.set_pixel(2, 0, brightness(75))
        time.sleep(delay)
        if height >= 2:
            hb.light_matrix.set_pixel(2, 0, brightness(100))
        time.sleep(delay)
        if height >= 3:
            hb.light_matrix.set_pixel(2, 1, brightness(75))
        time.sleep(delay)
        if height >= 4:
            hb.light_matrix.set_pixel(2, 1, brightness(100))
        time.sleep(delay)
        if height >= 5:
            hb.light_matrix.set_pixel(2, 2, brightness(75))
        time.sleep(delay)
        if height >= 6:
            hb.light_matrix.set_pixel(2, 2, brightness(100))
        time.sleep(delay)
        if height >= 7:
            hb.light_matrix.set_pixel(2, 3, brightness(75))
        time.sleep(delay)
        if height >= 8:
            hb.light_matrix.set_pixel(2, 3, brightness(100))
        time.sleep(delay)
        if height >= 9:
            hb.light_matrix.set_pixel(2, 4, brightness(75))
        time.sleep(delay)
        if height >= 10:
            hb.light_matrix.set_pixel(2, 4, brightness(100))

        
        hb.light_matrix.set_pixel(0, 0, brightness(50))
        hb.light_matrix.set_pixel(4, 0, brightness(50))
        hb.light_matrix.set_pixel(0, 4, brightness(50))
        hb.light_matrix.set_pixel(4, 4, brightness(50))

        time.sleep(1)

        if hb.left_button.was_pressed() or hb.right_button.was_pressed():
            brightness_multiplier = 2
    except SystemExit:
        break
    except KeyboardInterrupt:
        break
raise SystemExit

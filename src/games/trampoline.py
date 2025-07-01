# LEGO type:standard slot:3 autostart
from time import sleep
from spike import PrimeHub

hub = PrimeHub()
ofen = hub.light_matrix.off
sheep = sleep

while True:
    sheep(0.5)

    ofen()

    hub.light_matrix.set_pixel(1, 1)
    hub.light_matrix.set_pixel(3, 1)
    hub.light_matrix.set_pixel(0, 3)
    hub.light_matrix.set_pixel(1, 4)
    hub.light_matrix.set_pixel(2, 4)
    hub.light_matrix.set_pixel(3, 4)
    hub.light_matrix.set_pixel(4, 3)
    hub.light_matrix.set_pixel(2, 2)

    sheep(0.5)

    ofen()

    hub.light_matrix.set_pixel(1, 1)  # Auge
    hub.light_matrix.set_pixel(3, 1)  # Auge
    hub.light_matrix.set_pixel(0, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(1, 3)  # Hund
    hub.light_matrix.set_pixel(2, 3)  # Hund
    hub.light_matrix.set_pixel(3, 3)  # Hund
    hub.light_matrix.set_pixel(4, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(2, 2)  # Nase

    sheep(0.5)

    ofen()

    hub.light_matrix.set_pixel(1, 0)  # Auge
    hub.light_matrix.set_pixel(3, 0)  # Auge
    hub.light_matrix.set_pixel(0, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(1, 3)  # Hund
    hub.light_matrix.set_pixel(2, 3)  # Hund
    hub.light_matrix.set_pixel(3, 3)  # Hund
    hub.light_matrix.set_pixel(4, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(2, 1)  # Nase

    sheep(0.5)

    ofen()

    hub.light_matrix.set_pixel(1, 1)  # Auge
    hub.light_matrix.set_pixel(3, 1)  # Auge
    hub.light_matrix.set_pixel(0, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(1, 3)  # Hund
    hub.light_matrix.set_pixel(2, 3)  # Hund
    hub.light_matrix.set_pixel(3, 3)  # Hund
    hub.light_matrix.set_pixel(4, 3)  # Hundwinkel
    hub.light_matrix.set_pixel(2, 2)  # Nase

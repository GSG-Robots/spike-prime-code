# LEGO type:standard slot:5 autostart
import time
import hub as hb
from spike import PrimeHub
hub = PrimeHub()
cb = hb.button.center.callback()
hb.button.center.callback(lambda _: None)
yplayer = 4
hub.light_matrix.set_pixel(0, yplayer)
hub.left_button.was_pressed()
hb.button.center.was_pressed()
while not hub.left_button.was_pressed():
    if hb.button.center.was_pressed():
        yplayer = 3
        hub.light_matrix.off()
        hub.light_matrix.set_pixel(0, yplayer)
        time.sleep(1)
        yplayer = 4    
        hub.light_matrix.off()
        hub.light_matrix.set_pixel(0, yplayer)

hb.button.center.callback(cb)
# LEGO type:standard slot:9 autostart

import hub

SMILE = hub.Image("00000:09090:00000:90009:09990")
NEUTRAL = hub.Image("00000:09090:00000:09990:00000")
SAD = hub.Image("00000:09090:00000:09990:90009")

hub.display.align(hub.RIGHT)
hub.display.show(NEUTRAL)
hub.button.center.was_pressed()
while True:
    if hub.button.center.was_pressed():
        raise SystemExit
    if hub.button.left.was_pressed():
        hub.display.show(SAD)
    if hub.button.right.was_pressed():
        hub.display.show(SMILE)
 
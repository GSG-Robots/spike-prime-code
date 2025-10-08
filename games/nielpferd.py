# LEGO type:standard slot:3 autostart
import time
import hub

cb = hub.button.center.callback()
hub.button.center.callback(lambda _: None)

duration = 0.5

buttons.pressed(hub.button.POWER)
hub.button.left.was_pressed()
while not hub.button.right.was_pressed():
    hub.display.show(hub.Image("00000:90000:09990:90000:00000"))
    time.sleep(duration)
    hub.display.show(hub.Image("00000:09000:00999:09000:00000"))
    time.sleep(duration)

    if buttons.pressed(hub.button.POWER):
        duration = 0.07

    if hub.button.left.is_pressed() and hub.button.center.is_pressed() and hub.button.connect.is_pressed():
        with open("/flag.txt", "w") as f:
            f.write("LOCK active! Code: Left, Left, Right, Connect, Center")

        hub.power_off(restart=True)

    duration = min(0.7, max(0.075, duration))

hub.button.center.callback(cb)
raise SystemExit

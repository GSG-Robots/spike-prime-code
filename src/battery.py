# LEGO type:standard slot:8 autostart
"""Short run to show battery show"""

import time
import hub  # type: ignore # pylint: disable=import-error


def main():
    LOW = 8000
    HIGH = 8350  # actually unreachable 8360
    WAVEFORM = 1
    # Use 0 for "ah, ok", 1 for "oh, ok", 2 for "huh?" and 3 for "we are going to die"

    images = (
        hub.Image("00000:00000:00000:00000:00000"),  #   0 %
        hub.Image("00300:00000:00000:00000:00000"),  #  10 %
        hub.Image("00600:00000:00000:00000:00000"),  #  20 %
        hub.Image("00600:00300:00000:00000:00000"),  #  30 %
        hub.Image("00600:00600:00000:00000:00000"),  #  40 %
        hub.Image("00600:00600:00300:00000:00000"),  #  50 %
        hub.Image("00600:00600:00600:00000:00000"),  #  60 %
        hub.Image("00600:00600:00600:00300:00000"),  #  70 %
        hub.Image("00600:00600:00600:00600:00000"),  #  80 %
        hub.Image("00600:00600:00600:00600:00300"),  #  90 %
        hub.Image("00600:00600:00600:00600:00600"),  # 100 %
    )

    hub.sound.volume(100)
    hub.display.align(hub.FRONT)

    # Reset
    hub.button.center.was_pressed()

    while not hub.button.center.was_pressed():
        total_capacity = hub.battery.capacity_left()
        usable_capacity = round((hub.battery.voltage() - LOW) / (HIGH - LOW) * 100)
        height = usable_capacity // 10
        if usable_capacity <= 0:
            height = total_capacity // 10
            hub.led(9)
        elif usable_capacity < 100:
            hub.led(7)
        else:
            hub.led(6)
        is_charging = hub.battery.charger_detect()
        is_actively_charging = is_charging and usable_capacity < 100

        if is_actively_charging:
            for image in images[: height + 1]:
                hub.display.show(image)
                time.sleep(0.1)
                if hub.button.center.was_pressed():
                    raise SystemExit
        else:
            hub.display.show(images[height])

        time.sleep(2)

        if usable_capacity >= 100 and is_charging:
            hub.sound.beep(440, 500, WAVEFORM)
            time.sleep(0.5)
            hub.sound.beep(770, 875, WAVEFORM)
            time.sleep(0.75)


# <DISABLE BUTTON FOR INTERRUPT>
callback = hub.button.center.callback()
hub.button.center.callback(lambda i: ...)
try:
    main()
finally:
    # Reactivate button callback
    hub.button.center.callback(callback)
raise SystemExit

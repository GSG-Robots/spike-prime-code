# LEGO type:standard slot:10 autostart
import time

import hub

color_sensor = hub.port.A.device


color_sensor.mode([(5, 0)])
time.sleep(0.3)


LOWER = 190
MIDDLE = 487
UPPER = 590


def mesured_run(rev, l, u, speed):
    hub.port.C.motor.run_for_degrees(rev * 60, speed=speed)

    turns = 0
    low = None

    n = 1
    avg = color_sensor.get()[0]
    i, x = avg, avg

    while hub.port.C.motor.busy(1):
        ref = color_sensor.get()[0]
        if low is None:
            if ref > u:
                low = False
            elif ref < l:
                low = True
        elif low and ref > u:
            low = False
            turns += 1
        elif not low and ref < l:
            low = True
            turns += 1

        if ref < i:
            i = ref
        
        if ref > x:
            x = ref

        avg = ((avg * n) + ref) / (n + 1)
        n += 1

    return i, avg, x, turns


def calibrate(accuracy, speed):
    print("Estimating extremes...")
    i, m, x, _ = mesured_run(accuracy * 4, 0, 0, speed)

    print("Estimating upper bound...")
    a, b = round(m), round(x) + 10
    while not hub.button.left.is_pressed() and not abs(a - b) <= 1:
        *_, r = mesured_run(accuracy, m - 10, (a + b) // 2, speed)

        if r == accuracy:
            a = (a + b) // 2
        else:
            b = (a + b) // 2

        print("Next round... Upper: {u} ({a}, {b})".format(u=(a + b) // 2, a=a, b=b))
    u = a - 10
    
    print("Estimating lower bound...")
    a, b = round(i) - 10, round(m)
    while not hub.button.left.is_pressed() and not abs(a - b) <= 1:
        *_, r = mesured_run(accuracy, (a + b) // 2, u, speed)

        if r == accuracy:
            b = (a + b) // 2
        else:
            a = (a + b) // 2

        print("Next round... Lower: {l} ({a}, {b})".format(l=(a + b) // 2, a=a, b=b))
    l = b + 10

    print("Check values...")
    *_, r = mesured_run(accuracy * 4, l, u, speed)
    
    print("Lower: {l}, Upper: {u}".format(l=l, u=u))

    if r == accuracy * 4:
        print("Success!")
    else:
        print("Calibration failed.", r, accuracy * 4)

    return l, m, u

ll = 0
ms = []
uu = 1024
for x in range(1, 11):
    l, m, u = calibrate(2*6, x * 10)
    ll = max(l, ll)
    uu = min(u, uu)
    ms.append(m)

print()
print("LOWER = {l}".format(l=ll))
print("MIDDLE = {m}".format(m=sum(ms)/len(ms)))
print("UPPER = {u}".format(u=uu))

raise SystemExit

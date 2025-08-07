# LEGO type:standard slot:10 autostart
import time
import hub

color_sensor = hub.port.A.device
color_sensor.mode([(5, 0)])
time.sleep(0.3)

# LOWER = 190
# MIDDLE = 487
# UPPER = 590

LOWER = 175
MIDDLE = 402
UPPER = 588

def turn_rev(rev, speed, decel=1.3):
    decel *= 6
    rev *= 6
    p = speed / 100

    hub.port.C.motor.run_at_speed(speed)

    turns = 0
    low = None
    while not hub.button.left.is_pressed():
        gescheite_ref = color_sensor.get()[0]
        if low is None:
            if gescheite_ref > UPPER:
                low = False
            elif gescheite_ref < UPPER:
                low = True
        elif low and gescheite_ref > UPPER:
            low = False
            turns += 1
        elif not low and gescheite_ref < LOWER:
            low = True
            turns += 1
        
        print(rev, turns + (.5 if (low and gescheite_ref > MIDDLE) or (not low and gescheite_ref < MIDDLE) else 0))

        if decel >= (rev - turns):
            hub.port.C.motor.run_at_speed(speed * (rev - turns) / decel)

        if turns + (.5 if (low and gescheite_ref > MIDDLE) or (not low and gescheite_ref < MIDDLE) else 0) >= rev:
            break

    hub.port.C.motor.brake()

turn_rev(3, 100)
time.sleep(1)
turn_rev(3, -100)
time.sleep(1)
turn_rev(3, 100)

raise SystemExit

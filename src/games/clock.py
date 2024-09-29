# LEGO type:standard slot:2 autostart
import time
from spike import Motor

boot_time = (15, 22)
start_time = time.time()

hour_m = Motor("A")
minute_m = Motor("B")

hour_m.set_degrees_counted(0)
minute_m.set_degrees_counted(0)

def minute(time_m, speed=100):
    deg = ((time_m % 60) / 60 * 360)
    minute_m.run_to_position(round(deg), speed=speed)

def hour(time_h, speed=100):
    deg = ((time_h % 12) / 12 * 360)
    hour_m.run_to_position((360-round(deg)) % 360, speed=speed)

def show_time(time_=None, speed=10):
    print(1, time_)
    if time_ is None:
        time_ = time.time()
    if not isinstance(time_, tuple):
        timein_m = (time_ - start_time) / 60
        btimein_m = boot_time[0] * 60 + boot_time[1]
        ttimein_m = timein_m + btimein_m
        time_h = ttimein_m // 60 % 24
        time_m = ttimein_m % 60
        time_ = time_h, time_m
    print(2, time_)
    hour((time_[0] % 12), speed=speed)
    minute(time_[1], speed=speed)

show_time((0, 0), speed=100)
show_time((3, 45), speed=100)
show_time((6, 30), speed=100)
show_time((9, 15), speed=100)
show_time((0, 0), speed=100)
show_time(speed=100)

while True:
    show_time(speed=20)
    try:
        time.sleep(1)
    except KeyboardInterrupt as e:
        raise SystemExit from e

# LEGO type:standard slot:2 autostart
import time
from spike import Motor, PrimeHub

import hub
import time

class Communicator:
    def __init__(self, port: int):
        self.conn = hub.USB_VCP(port)
        self.conn.init(flow=3)
        
    def _readline(self) -> bytes:
        while True:
            line = self.conn.readline()
            if line is not None:
                return line
        
    def get(self) -> str:
        while True:
            for line in self._readline().decode("utf-8").splitlines():
                if line.startswith("GSGR:"):
                    return line[5:]
                
    def send(self, data: str):
        self.conn.write("GSGR:{data}\r\n".format(data=data).encode("utf-8"))
        
    def getall(self):
        while True:
            yield self.get()
            

communicator = Communicator(0)
CURRENT_TIME = time.time()

hour_m = Motor("A")
minute_m = Motor("B")

hour_m.set_degrees_counted(0)
minute_m.set_degrees_counted(0)


def minute(time_m, speed=100):
    deg = (time_m % 60) / 60 * 360
    minute_m.run_to_position(round(deg), speed=speed)


def hour(time_h, speed=100):
    deg = (time_h % 12) / 12 * 360
    hour_m.run_to_position((360 - round(deg)) % 360, speed=speed)


def show_time(time_=None, speed=10):
    print(1, time_)
    if time_ is None:
        time_ = CURRENT_TIME + time.time()
    if not isinstance(time_, tuple):
        timein_m = (time_) / 60
        time_h = timein_m // 60 % 24
        time_m = timein_m % 60
        time_ = time_h, time_m
    print(2, time_)
    hour((time_[0] % 12), speed=speed)
    minute(time_[1], speed=speed)


show_time((0, 0), speed=100)
show_time((3, 45), speed=100)
show_time((6, 30), speed=100)
show_time((9, 15), speed=100)
show_time((0, 0), speed=100)


# show_time(speed=100)

# curtime = ""

while True:
    # res = vCOM.read()
    # if res is not None:
    #     try:
    #         curtime += res.decode("utf-8")
    #         parts = curtime.split("\n")
    #         if len(parts) > 1:
    #             start_time = round(float(parts[-2].strip()))
    #             CURRENT_TIME = start_time - time.time()
    #             curtime = parts[-1]
    #     except Exception as e:
    #         PrimeHub().light_matrix.write(str(e))
    #         raise e
    # show_time(speed=20)
    try:
        line = None
        communicator.send("get_time")
        while True:
            line = communicator.get()
            if not line.startswith("time:"):
                continue
            else:
                line = line[5:]
            parts = line.split(":")
            if len(parts) != 2:
                continue
            break
        try:
            h, m = int(parts[0]), int(parts[1])
            print(h, m)
            show_time((h, m), speed=20)
        finally:
            time.sleep(10)
    except KeyboardInterrupt as e:
        raise SystemExit from e

import time
from typing import Generator
import serial


class Communicator:
    def __init__(self, port):
        self.conn = serial.Serial(port)
        
    def get(self) -> str:
        while True:
            for line in self.conn.readline().decode("utf-8").splitlines():
                if line.startswith("GSGR:"):
                    return line[5:]
                
    def send(self, data: str):
        self.conn.write(f"GSGR:{data}\r\n".encode("utf-8"))

    def getall(self):# -> Generator[str]:
        while True:
            yield self.get()


communicator = Communicator("COM3")
def send_time():
    hour, minute = time.localtime().tm_hour, time.localtime().tm_min
    communicator.send(f"time:{hour:02}:{minute:02}")
    print(f"Sent {hour:02}:{minute:02}")
    

send_time()
for line in communicator.getall():
    print(line)
    if line == "get_time":
        send_time()

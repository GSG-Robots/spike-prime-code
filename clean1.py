# LEGO type:standard slot:3
from spike import Motor, PrimeHub, MotorPair

hub = PrimeHub()


pair =MotorPair("F", "E")

m = Motor("D")
m.run_to_position(0, speed=100)
m.set_stall_detection(True)

def forward(cm):
    pair.move(cm * -1, unit="cm", steering=0, speed=100)

# while True:
#     m.run_to_position(50, speed=10)
#     m.run_to_position(360-50, speed=10)
#     if m.was_stalled():
#         raise SystemExit()
forward(20)

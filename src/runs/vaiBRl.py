import time
import hub
from gsgr.conditions import OR, cm, impact, light_left, light_right, pickup, sec
from gsgr.enums import Color, Pivot, Sensor
from gsgr.movement import gyro_drive, gyro_set_origin, gyro_turn

display_as = 2
color = Color.BLUE

left_sensor = Sensor.LIGHT
right_sensor = Sensor.LIGHT


def run():
    # Set Gyro Origin
    gyro_set_origin()
    gyro_drive(0, 70, OR(light_left(70, True), light_right(70, True)))
    hub.led(6)
    

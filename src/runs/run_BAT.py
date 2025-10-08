import time

import color as col

import hub

display_as = "bat"
color = col.WHITE


def run():
    hub.light_matrix.write(str(hub.battery_voltage()))
    time.sleep(2.5)

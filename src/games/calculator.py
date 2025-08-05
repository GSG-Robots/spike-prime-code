# LEGO type:standard slot:12 autostart


import hub as hb
from spike import PrimeHub

hub = PrimeHub()


cb = hb.button.center.callback()
hb.button.center.callback(lambda _: None)


current_operator = 0
solution = 0
operators = ["+", "-", "*", "/"]
numbers = [
    hb.Image("09990:09090:09090:09090:09990"),
    hb.Image("00900:09900:00900:00900:09990"),
    hb.Image("09990:00090:09990:09000:09990"),
    hb.Image("09990:00090:09990:00090:09990"),
    hb.Image("09090:09090:09990:00090:00090"),
    hb.Image("09990:09000:09990:00090:09990"),
    hb.Image("09990:09000:09990:09090:09990"),
    hb.Image("09990:00090:00900:09000:09000"),
    hb.Image("09990:09090:09990:09090:09990"),
    hb.Image("09990:09090:09990:00090:09990"),
    hb.Image("90999:90909:90909:90909:90999"),
    hb.Image("90090:90990:90090:90090:90999"),
    hb.Image("90999:90009:90999:90900:90999"),
    hb.Image("90999:90009:90999:90009:90999"),
    hb.Image("90909:90909:90999:90009:90009"),
    hb.Image("90999:90900:90999:90009:90999"),
    hb.Image("90999:90900:90999:90909:90999"),
    hb.Image("90999:90009:90090:90900:90900"),
    hb.Image("90999:90909:90999:90909:90999"),
    hb.Image("90999:90909:90999:90009:90999"),
]


def write(number):
    if 0 <= number <= 19:
        hb.display.show(numbers[number])
    else:
        hub.light_matrix.write(number)

def select():
    number = 0
    write(number)
    hub.left_button.was_pressed()
    hub.right_button.was_pressed()
    hb.button.center.was_pressed()
    while not hb.button.center.was_pressed():
        if hub.left_button.was_pressed():
            number -= 1
            write(number)

        if hub.right_button.was_pressed():
            number += 1
            write(number)
    
    return number

number1 = select()

hub.light_matrix.write(operators[current_operator])
hub.left_button.was_pressed()
hub.right_button.was_pressed()
hb.button.center.was_pressed()

while not hb.button.center.was_pressed():
    if hub.left_button.was_pressed():
        current_operator -= 1
        current_operator = current_operator % 4
        hub.light_matrix.write(operators[current_operator])

    if hub.right_button.was_pressed():
        current_operator += 1
        current_operator = current_operator % 4
        hub.light_matrix.write(operators[current_operator])


number2 = select()

if current_operator == 0:
    solution = number1 + number2
elif current_operator == 1:
    solution = number1 - number2
elif current_operator == 2:
    solution = number1 * number2
elif current_operator == 3:
    solution = number1 / number2

hub.light_matrix.write(solution)
while not hb.button.center.was_pressed():
    ...


hb.button.center.callback(cb)
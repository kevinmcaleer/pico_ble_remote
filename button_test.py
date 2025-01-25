from machine import Pin
from time import sleep

button_left = Pin(2, Pin.IN, Pin.PULL_UP)
button_right = Pin(3, Pin.IN, Pin.PULL_UP)
button_x = Pin(4, Pin.IN, Pin.PULL_UP)
button_y = Pin(5, Pin.IN, Pin.PULL_UP)
button_up = Pin(8, Pin.IN, Pin.PULL_UP)
button_down= Pin(9, Pin.IN, Pin.PULL_UP)
button_a = Pin(6, Pin.IN, Pin.PULL_UP)
button_b = Pin(7, Pin.IN, Pin.PULL_UP)
button_menu= Pin(10, Pin.IN, Pin.PULL_UP)
button_select = Pin(11, Pin.IN, Pin.PULL_UP)
button_start = Pin(12, Pin.IN, Pin.PULL_UP)

while True:
#     print(f"Button Status, A: {button_a.value()}, B: {button_b.value()}, X: {button_x.value()}, {count}")
    if button_left.value() == 0:
        print("Left pressed")
    if button_right.value() == 0:
        print("Right pressed")
    if button_x.value() == 0:
        print("X pressed")
    if button_y.value() == 0:
        print("Y pressed")
    if button_up.value() == 0:
        print("Up pressed")
    if button_down.value() == 0:
        print("Down pressed")
    if button_a.value() == 0:
        print("A pressed")
    if button_b.value() == 0:
        print("B pressed")
    if button_menu.value() == 0:
        print("Menu pressed")
    if button_start.value() == 0:
        print("Start pressed")
    if button_select.value() == 0:
        print("Select pressed")
    sleep(0.25)
    count += 1
from machine import Pin
from time import sleep

names = ["up", "down", "right", "left", "A", "B"]

button_up = Pin(14, Pin.IN, Pin.PULL_UP)
button_down = Pin(13, Pin.IN, Pin.PULL_UP)
button_right = Pin(12, Pin.IN, Pin.PULL_UP)
button_left = Pin(11, Pin.IN, Pin.PULL_UP)
button_A = Pin(10, Pin.IN, Pin.PULL_UP)
button_B = Pin(9, Pin.IN, Pin.PULL_UP)
buttons = [button_up, button_down, button_right, button_left, button_A, button_B]

last = [5]*len(names)

print("LED starts flashing...")

while True:
    for i in range(len(names)):
        newval = buttons[i].value()
        if last[i] != newval:
            last[i]=newval
            if newval==0:
                print(names[i]+" on")
            else:
                print(names[i]+" off") 

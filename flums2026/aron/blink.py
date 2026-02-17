from machine import Pin
from time import sleep

pin = Pin(25, Pin.OUT)

print("LED starts flashing...")


for i in range(0, 10):
    pin.toggle()
    sleep(0.2)
pin.value(0)


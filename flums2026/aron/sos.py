from machine import Pin
from time import sleep

pin = Pin(15, Pin.OUT)

print("LED starts flashing...")


for i in range(0,6):
    pin.toggle()
    sleep(0.2)
pin.value(0)
sleep(0.4)
for i in range(0, 6):
    pin.toggle()
    sleep(0.5)
pin.value(0)
for i in range(0, 6):
    pin.toggle()
    sleep(0.2)
pin.value(0)
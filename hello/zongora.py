from utime import time_ns
from machine import Pin
import time

hangsz = Pin(26, Pin.OUT)
gomb1 = Pin(17, Pin.IN, Pin.PULL_DOWN)
gomb2 = Pin(16, Pin.IN, Pin.PULL_DOWN)
gomb3 = Pin(12, Pin.IN, Pin.PULL_DOWN)

while True:
    if gomb1.value() == 1:
        hangsz.toggle()
        # time.sleep(0.001)
        time.sleep_us(999)
    if gomb2.value() == 1:
        hangsz.toggle()
        time.sleep(0.002)
    if gomb3.value() == 1:
        hangsz.toggle()
        time.sleep(0.003)








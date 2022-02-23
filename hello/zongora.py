from utime import time_ns
from machine import Pin
import time

hangsz = Pin(26, Pin.OUT)
gomb1 = Pin(17, Pin.IN, Pin.PULL_DOWN)
gomb2 = Pin(16, Pin.IN, Pin.PULL_DOWN)
gomb3 = Pin(12, Pin.IN, Pin.PULL_DOWN)
gomb4 = Pin(21, Pin.IN, Pin.PULL_DOWN)
gomb5 = Pin(7, Pin.IN, Pin.PULL_DOWN)

while True:
    if gomb1.value() == 1:
        hangsz.toggle()
        time.sleep_us(919)
    if gomb2.value() == 1:
        hangsz.toggle()
        time.sleep_us(975)
    if gomb3.value() == 1:
        hangsz.toggle()
        time.sleep_us(1099)
    if gomb4.value() == 1:
        hangsz.toggle()
        time.sleep_us(975)
    if gomb5.value() == 1:
        hangsz.toggle()
        time.sleep_us(1099)








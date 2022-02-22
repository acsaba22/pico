from machine import Pin

import time

piros = Pin(0, Pin.OUT)
zold = Pin(1, Pin.OUT)
kek = Pin(2, Pin.OUT)
pirosgomb=Pin(16, Pin.IN, Pin.PULL_UP)
zoldgomb=Pin(17, Pin.IN, Pin.PULL_UP)
kekgomb=Pin(18, Pin.IN, Pin.PULL_UP)
piros.on()
zold.on()
kek.on()


while True:
    print(zoldgomb.value())
    time.sleep_ms(100)

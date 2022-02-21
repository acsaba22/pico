from machine import Pin

import time

piros = Pin(0, Pin.OUT)
zold = Pin(1, Pin.OUT)
kek = Pin(2, Pin.OUT)
zold.on()
kek.on()
piros.on()

ido = 1
while True:
                piros.on()
                kek.off()
                time.sleep(ido)
                kek.on()
                piros.off()
                time.sleep(ido)
                ido = ido - 0.02
                

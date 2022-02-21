from machine import Pin

import time

piros = Pin(0, Pin.OUT)
zold = Pin(1, Pin.OUT)
kek = Pin(2, Pin.OUT)
piros.on()
zold.on()
kek.on()
piros.on()

time.sleep(2)
piros.off()

time.sleep(2)

while True:
    veg_ido = time.time() + 3
    while time.time() < veg_ido:
                    piros.off()
                    time.sleep(0.001)
                    piros.on()
                    time.sleep(0.001)

    veg_ido = time.time() + 3
    while time.time() < veg_ido:
                    piros.off()
                    time.sleep(0.001)
                    piros.on()
                    time.sleep(0.001)


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
    for i in range(100):
        for _ in range(500):
                    piros.off()
                    time.sleep_us(i)
                    piros.on()
                    time.sleep_us(100-i)
                    
    zold.off()
    time.sleep(1)
    zold.on()
                    
    veg_ido = time.time() + 3
    while time.time() < veg_ido:
                    piros.off()
                    time.sleep_us(100+i)
                    piros.on()
                    time.sleep_us(i)


from machine import Pin

import time

piros = Pin(0, Pin.OUT)
zold = Pin(1, Pin.OUT)
kek = Pin(2, Pin.OUT)
zold.on()
kek.on()
piros.on()
time.sleep(1)
while True:                   
                piros.off()
                time.sleep(1)
                zold.off()
                time.sleep(1)
                piros.on() 
                time.sleep(3)
                piros.off()
                time.sleep(1)
                zold.on()
                time.sleep(3)




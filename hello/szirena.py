from machine import Pin
import time

kek = Pin(15, Pin.OUT)
piros = Pin(14, Pin.OUT)

kek.off()
piros.off()

while True:
    kek.on()
    time.sleep(0.01)
    kek.off()
    piros.on()
    time.sleep(0.01)
    piros.off()

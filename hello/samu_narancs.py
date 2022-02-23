from machine import Pin, PWM

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

piros.off()

piros = PWM(Pin(0))
piros.freq(100000)
zold = PWM(Pin(1))
zold.freq(100000)
kek = PWM(Pin(2))
kek.freq(100000)

zold_fenyero = 0
kek_fenyero = 0
piros_fenyero = 0

zold.duty_u16(zold_fenyero)  # 0..65535
kek.duty_u16(kek_fenyero)
piros.duty_u16(piros_fenyero)
while True:
    if pirosgomb.value() == 0:
        piros_fenyero += 2048
        if piros_fenyero > 65535:
            piros_fenyero = 0
        piros.duty_u16(piros_fenyero)

    if zoldgomb.value() == 0:
        zold_fenyero += 2048
        if zold_fenyero > 65535:
            zold_fenyero = 0
        zold.duty_u16(zold_fenyero)

    if kekgomb.value() == 0:
        kek_fenyero += 2048
        if kek_fenyero > 65535:
            kek_fenyero = 0
        kek.duty_u16(kek_fenyero)
        
    print(piros_fenyero, zold_fenyero, kek_fenyero)
    time.sleep(0.2)


stop


while True:
        zold.off()
        time.sleep_us(1000)
        zold.on()
        time.sleep_us(1300)
        
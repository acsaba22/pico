import neopixel
import machine
from time import sleep


p = machine.Pin(0, machine.Pin.OUT)
n = neopixel.NeoPixel(p, 60)
speed=0.001
times=5

for w in range(times):
    for t in range(0,60):
        for i in range(0,60):
            if t==i:
                n[i] = (i , 0 , 60-i )
            else:
                n[i]=(0 ,0 ,0 )
        n.write()
        sleep(speed)

    for t in range(0,60):
        for i in range(0,60):
            if 59-t==i:
                n[i] = (i , 0 , 60-i )
            else:
                n[i]=(0 ,0 ,0 )
        n.write()
        sleep(speed)
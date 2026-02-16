import neopixel
import machine

LEDNUM = 32

p = machine.Pin(0, machine.Pin.OUT)
n = neopixel.NeoPixel(p, LEDNUM)


# Draw a red gradient.
for i in range(LEDNUM):
    n[i] = (i, 0, 0)

# Update the strip.
n.write()

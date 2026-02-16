import neopixel
import machine

p = machine.Pin(0, machine.Pin.OUT)
n = neopixel.NeoPixel(p, 32)


# Draw a red gradient.
for i in range(32):
    n[i] = (0, 0, 0)

# Update the strip.
n.write()

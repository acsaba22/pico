import sys
if "/lib" not in sys.path:
    sys.path.append("/lib")

import math
import lcd

MAX_ITERATION = 100
ABS_LIMIT = 100

rFreq = 3
gFreq = 5
bFreq = 8

def color(mandelColor):
  r = math.sin(rFreq*mandelColor)/2+0.5
  g = math.sin(gFreq*mandelColor)/2+0.5
  b = math.sin(bFreq*mandelColor)/2+0.5
  ret = int((2**5)*r)
  ret <<= 6
  ret |= int((2**5)*g)
  ret <<= 5
  ret |= int((2**6)*b)
  return ret

COLORS=[color(i/MAX_ITERATION) for i in range(MAX_ITERATION+1)]

def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z**2 + c
    return step

def draw_mandelbrot(lcd):
    zoom = 0.004
    step = 16
    zs = zoom*step
    buffer = bytearray(480*2)
    sx = (-240-240)*zoom
    my = (-160)*zoom
    for y in range(0, 160, step): #159, -1, -step):
        mx = sx
        my = (y-160)*zoom
        #my += zs
        for x in range(0, 480, step):
            c = COLORS[mandelbrot(mx, my)]
            mx += zs
            for s in range(step):
                buffer[(x<<1)+s*2] = c>>8
                buffer[(x<<1)+s*2+1] = c&0xFF
        for s in range(step):
            lcd.show_buffer(0, y+s, 479, y+s, bytearray(buffer))
        for s in range(step):
            lcd.show_buffer(0, 319-y-s, 479, 319-y-s, bytearray(buffer))

def main():
    screen = lcd.LCD_3inch5()
    screen.bl_ctrl(100)
    draw_mandelbrot(screen)
    while True:
        time.sleep(0.1)

if __name__=='__main__':
    main()
import liblcd

import math

MAX_ITERATION = 100
ABS_LIMIT = 100

rFreq = 3
gFreq = 5
bFreq = 8

def color(mandelColor):
  r = math.sin(rFreq*mandelColor)/2+0.5
  g = math.sin(gFreq*mandelColor)/2+0.5
  b = math.sin(bFreq*mandelColor)/2+0.5
  ret = int((2**5)*b)
  ret <<= 5
  ret |= int((2**5)*r)
  ret <<= 6
  ret |= int((2**6)*g)
  return ret

COLORS=[color(i/MAX_ITERATION) for i in range(MAX_ITERATION+1)]

def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z*z + c
    return step

def draw_mandelbrot(lcd, step=1):
    zoom = 0.004
    zoom = 0.01
    # step = 8
    offset = (0*-240, 0)
    zs = zoom*step
    buffer = bytearray(480*2)
    sx = (offset[0]-240)*zoom
    for y in range(0, 160, step): #159, -1, -step):
        mx = sx
        my = (y-160)*zoom
        #my += zs
        for x in range(0, 480, step):
            c = COLORS[mandelbrot(mx, my)]
            mx += zs
            for s in range(step):
                buffer[(x<<1)+(s<<1)] = c>>8
                buffer[(x<<1)+(s<<1)+1] = c&0xFF
        for s in range(step):
            lcd.ShowBuffer(0, 479, y+s, y+s, buffer)
        for s in range(step):
            lcd.ShowBuffer(0, 479, 319-y-s, 319-y-s, buffer)

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    for step in (16, 4, 1):
        draw_mandelbrot(screen, step)

if __name__=='__main__':
    main()
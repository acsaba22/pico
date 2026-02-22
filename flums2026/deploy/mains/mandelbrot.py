import jobs
import timestats

import liblcd

import math
from ulab import numpy as np

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

def mandelbrot_tensor(xmin, xmax, ymin, ymax, width, height, max_iter):
    # initialize real and complex grid
    x = np.linspace(xmin, xmax, width)
    y = np.zeros(height, dtype=complex)
    y.imag=np.linspace(ymin, ymax, height)
    xx, yy = np.meshgrid(x, y)
    c_matrix = xx + yy
    # initialize image tensor and z matrix
    z_matrix = np.zeros((height, width), dtype=complex)
    max_iter_tensor = np.zeros((max_iter, height, width))
    for n in range(max_iter-1):
        will_update = np.abs(z_matrix) <= 2
        z_updated = (z_matrix * z_matrix + c_matrix)*will_update 
        z_not_updated = (1-will_update)*z_matrix
        z_matrix = z_updated + z_not_updated
        max_iter_tensor[n+1] = max_iter_tensor[n] + will_update
    return max_iter_tensor

def mandelbrot_line(cx, cy, width):
    res = [MAX_ITERATION] * width
    for i in range(width):
        res[i] = mandelbrot(cx[i], cy[i])
    return res

def mandelbrot_line2(cx, cy, width):
    zx = np.zeros(width)
    zy = np.zeros(width)

    limit = ABS_LIMIT*ABS_LIMIT
    max_iter_tensor = np.zeros(width, dtype=np.int8)
    for i in range(0, MAX_ITERATION-1):
        abs2_values = zx * zx + zy * zy
        will_update = abs2_values < limit
        new_zx = ((zx * zx) - (zy * zy) + cx) * will_update
        new_zy = (2 * zx * zy + cy) * will_update
        zx_not_updated = (1-will_update)*zx
        zy_not_updated = (1-will_update)*zy
        zx = new_zx + zx_not_updated
        zy = new_zy + zy_not_updated
        max_iter_tensor = max_iter_tensor + will_update
        
        # for j, v in enumerate(abs_values):
        #     if v >= ABS_LIMIT and res[j] == MAX_ITERATION: res[j] = i
    return max_iter_tensor


def mandelbrot_line3(cx, cy, width):
    zx = np.zeros(width)
    zy = np.zeros(width)

    limit = ABS_LIMIT*ABS_LIMIT
    max_iter_tensor = np.zeros(width, dtype=np.int8)
    for i in range(0, MAX_ITERATION-1):
        abs2_values = zx * zx + zy * zy
        will_update = abs2_values < limit
        max_iter_tensor = max_iter_tensor + will_update
        new_zx = ((zx * zx) - (zy * zy) + cx)
        new_zy = (2 * zx * zy + cy)
        zx = new_zx
        zy = new_zy
        
        # for j, v in enumerate(abs_values):
        #     if v >= ABS_LIMIT and res[j] == MAX_ITERATION: res[j] = i
    return max_iter_tensor

def mandelbrot_line4(cx, cy, width):
    zx = np.zeros(width)
    zy = np.zeros(width)

    limit = ABS_LIMIT*ABS_LIMIT
    max_iter_tensor = np.zeros(width, dtype=np.int8)
    for i in range(0, MAX_ITERATION-1):
        abs2_values = zx **2 + zy **2
        will_update = abs2_values < limit
        max_iter_tensor = max_iter_tensor + will_update
        new_zx = ((zx **2) - (zy **2) + cx)
        new_zy = (2 * zx * zy + cy)
        zx = new_zx
        zy = new_zy
        
        # for j, v in enumerate(abs_values):
        #     if v >= ABS_LIMIT and res[j] == MAX_ITERATION: res[j] = i
    return max_iter_tensor

methods = [mandelbrot_line, mandelbrot_line2, mandelbrot_line3, mandelbrot_line4]

def draw_mandelbrot2(lcd, step=1):
    zoom = 0.004
    zoom = 0.01
    # step = 8
    offset = (0*-240, 0)
    zs = zoom*step
    buffer = bytearray(480*2)
    sx = (offset[0]-240)*zoom
    width = 480//step
    cx = np.zeros(width)
    cy = np.zeros(width)
    x = sx
    for i in range(width):
        cx[i] = x
        x  += zs
    
    timers = [timestats.NewTimer("%s_%d" % (f.__name__, step)) for f in methods]
    num_methods = len(methods)
    for y in range(0, 160, step): #159, -1, -step):
        my = (y-160)*zoom
        cy = np.ones(width) * my
        #my += zs


        i = (y//step)%num_methods
        with timers[i]:
            r = methods[i](cx, cy, width)
        x = 0
        for v in r:
            if x >= 480: break
            c = COLORS[v]
            for s in range(step):
                buffer[(x<<1)+(s<<1)] = c>>8
                buffer[(x<<1)+(s<<1)+1] = c&0xFF
            x += step
        for s in range(step):
            lcd.ShowBuffer(0, 479, y+s, y+s, buffer)
            lcd.ShowBuffer(0, 479, 319-y-s, 319-y-s, buffer)


async def mandelmain():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    for step in (16,4,2,1):
        xmin, xmax, ymin, ymax = -2.0, 1.0, -1.5, 1.5
        width, height = 120, 80
        max_iter = 24
        draw_mandelbrot2(screen, step)
        timestats.stats.report()

async def runall():
    jobs.start(mandelmain())
    jobs.start(timestats.stats.run())
    await jobs.STOP.wait()

def main():
    jobs.runMain(runall())

if __name__ == '__main__':
    main()

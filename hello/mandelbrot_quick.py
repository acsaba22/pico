
import liblcd
import math

import framebuf
import time
import os

LCD = liblcd.LCD_3inch5()


MAX_ITERATION = 100
ABS_LIMIT = 100


red = 0xf800
green = 0x07e0
blue = 0x001f

def color(r,g,b):
    ret = int((2**5)*r)
    ret <<= 6
    ret |= int((2**6)*g)
    ret <<= 5
    ret |= int((2**5)*b)
    return ret

rFreq = 3
gFreq = 5
bFreq = 8

def calcColor(step):
    mandelColor = step / MAX_ITERATION
    r = math.sin(rFreq*mandelColor)/2+0.5
    g = math.sin(gFreq*mandelColor)/2+0.5
    b = math.sin(bFreq*mandelColor)/2+0.5
    return color(r,g,b)


colors = []


def initColors():
    # colors = []
    for i in range(MAX_ITERATION+1):
        colors.append(calcColor(i))


def getColor(step):
    return colors[step]


def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z*z + c
    return step


def getPixelStep(x, y):
    return mandelbrot((x/480-0.5)*4.8, (y/320-0.5)*3.2)


maxBufP = 10000
buf = bytearray(maxBufP*2)
bufPos = 0


def resetBuf():
    global bufPos
    bufPos = 0

def writeColor(color):
    global bufPos
    global buf
    buf[bufPos] = color >> 8
    buf[bufPos+1] = color & 0xff
    bufPos = bufPos + 2


def repeatColor(color, n):
    global bufPos
    global buf
    resetBuf()
    a = color >> 8
    b = color & 0xff
    for i in range(n):
        buf[bufPos] = a
        buf[bufPos+1] = b
        bufPos = bufPos + 2


def DrawRec(x1, x2, y1, y2, v11, v12, v21, v22):
    global LCD
    if y1 == y2:
        resetBuf()
        col = getColor(v11)
        writeColor(col)
        x = x1+1
        while x <= x2:
            if x == x2:
                col = getColor(v21)
            else:
                col = getColor(getPixelStep(x, y1))
            writeColor(col)
            x += 1
        LCD.ShowBuffer(x1, x2, y1, y1, buf[:bufPos])
        return

    if y1 == y2-1:
        DrawRec(x1, x2, y1, y1, v11, v11, v21, v21)
        DrawRec(x1, x2, y2, y2, v12, v12, v22, v22)
        return

    xo = (x1+x2)//2
    yo = (y1+y2)//2
    v1o = getPixelStep(x1, yo)
    vo1 = getPixelStep(xo, y1)
    voo = getPixelStep(xo, yo)
    vo2 = getPixelStep(xo, y2)
    v2o = getPixelStep(x2, yo)

    if v11 == v22 and v11 == v2o and v11 == v21 and v11 == vo2 and v11 == voo and v11 == vo1 and v11 == v12 and v11 == v1o:
        col = getColor(v11)
        repeatColor(col, (x2-x1+1)*(y2-y1+1))
        LCD.ShowBuffer(x1, x2, y1, y2, buf[:bufPos])
        return

    DrawRec(x1, xo, y1, yo, v11, v1o, vo1, voo)
    DrawRec(x1, xo, yo, y2, v1o, v12, voo, vo2)
    DrawRec(xo, x2, y1, yo, vo1, voo, v21, v2o)
    DrawRec(xo, x2, yo, y2, voo, vo2, v2o, v22)


WWW = 480
HHH = 320

def DrawAll():
    w = WWW-1
    h = HHH-1
    DrawRec(0, w, 0, h, getPixelStep(0, 0), getPixelStep(
        w, 0), getPixelStep(0, h), getPixelStep(w, h))


def DrawSlow():
    global LCD
    for x in range(WWW):
        l = []
        for y in range(HHH):
            col = getColor(getPixelStep(x, y))
            l = l + [col >> 8, col & 0xff]
        LCD.ShowBuffer(x, x, 0, 319, bytearray(l))



class CoopDraw:
    def __init__(self):
        pass


def main():
    global LCD
    LCD.BackLight(100)

    initColors()

    start = time.time()
    print('hello')
    DrawAll()

    print('total time', time.time()-start)



if __name__ == '__main__':
    main()


import liblcd
import math

import framebuf
import time
import os
import sys

LCD = liblcd.LCD_3inch5()


MAX_ITERATION = 100
ABS_LIMIT = 100


red = 0xf800
green = 0x07e0
blue = 0x001f


def rgbToColor(r, g, b):
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
    return rgbToColor(r, g, b)


colors = []


def initColors():
    global colors
    colors = []
    for i in range(MAX_ITERATION+1):
        colors.append(calcColor(i))


def getColor(step):
    return colors[step]


def mandelbrot(x, y):
    return x+y%100
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z**2 + c
    return step


def getPixelStep(x, y):
    return mandelbrot((x/480-0.5)*4.8, (y/320-0.5)*3.2)


class Window:
    def __init__(self, maxPixelNum):
        self.maxPixelNum = maxPixelNum
        # self.buf = memoryview(bytearray(self.maxPixelNum*2))
        self.buf = bytearray(self.maxPixelNum*2)
        self.bufPos = 0

    def resetBuf(self):
        self.bufPos = 0

    def writeColor(self, color):
        self.buf[self.bufPos] = color >> 8
        self.buf[self.bufPos+1] = color & 0xff
        self.bufPos = self.bufPos + 2

    def repeatColor(self, color, n):
        self.resetBuf()
        a = color >> 8
        b = color & 0xff
        for i in range(n):
            self.buf[self.bufPos] = a
            self.buf[self.bufPos+1] = b
            self.bufPos = self.bufPos + 2

    def content(self):
        return self.buf[:self.bufPos]

    def setLocation(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2
        self.width = x2 - x1
        self.height = y2 - y1
        size = self.width*self.height
        if self.maxPixelNum <= size:
            print('ERROR: to big window:', size)
            sys.exit()
        self.bufPos = self.width*self.height*2

    def putPixel(self, x, y, color):
        row = y - self.y1
        pixel = x-self.x1 + row*self.width
        self.buf[pixel<<1] = color >> 8
        self.buf[(pixel<<1)+1] = color & 0xff
        pass

    def fill(self, color):
        for x in range(self.x1, self.x2+1):
            for y in range(self.y1, self.y2+1):
                self.putPixel(x, y, color)
        pass

    def render(self):
        LCD.ShowBuffer(self.x1, self.x2, self.y1, self.y2, window.content())


window = Window(5000)


# def DrawRec(x1, x2, y1, y2, v11, v12, v21, v22):
#     global LCD
#     if y1 == y2:
#         window.resetBuf()
#         col = getColor(v11)
#         window.writeColor(col)
#         x = x1+1
#         while x <= x2:
#             if x == x2:
#                 col = getColor(v21)
#             else:
#                 col = getColor(getPixelStep(x, y1))
#             window.writeColor(col)
#             x += 1
#         print('here3')
#         LCD.ShowBuffer(x1, x2, y1, y1, window.content())
#         return

#     if y1 == y2-1:
#         DrawRec(x1, x2, y1, y1, v11, v11, v21, v21)
#         DrawRec(x1, x2, y2, y2, v12, v12, v22, v22)
#         return

#     xo = (x1+x2)//2
#     yo = (y1+y2)//2
#     v1o = getPixelStep(x1, yo)
#     vo1 = getPixelStep(xo, y1)
#     voo = getPixelStep(xo, yo)
#     vo2 = getPixelStep(xo, y2)
#     v2o = getPixelStep(x2, yo)

#     if v11 == v22 and v11 == v2o and v11 == v21 and v11 == vo2 and v11 == voo and v11 == vo1 and v11 == v12 and v11 == v1o:
#         col = getColor(v11)
#         n = (x2-x1+1)*(y2-y1+1)
#         if n <  window.maxPixelNum:
#             print('repeatColor', n)
#             window.repeatColor(col, (x2-x1+1)*(y2-y1+1))
#             LCD.ShowBuffer(x1, x2, y1, y2, window.content())
#             return

#     DrawRec(x1, xo, y1, yo, v11, v1o, vo1, voo)
#     DrawRec(x1, xo, yo, y2, v1o, v12, voo, vo2)
#     DrawRec(xo, x2, y1, yo, vo1, voo, v21, v2o)
#     DrawRec(xo, x2, yo, y2, voo, vo2, v2o, v22)


WWW = 480
HHH = 320


# def DrawAll():
#     w = WWW-1
#     h = HHH-1
#     DrawRec(0, w, 0, h, getPixelStep(0, 0), getPixelStep(
#         w, 0), getPixelStep(0, h), getPixelStep(w, h))


def DrawSlow():
    global LCD
    for x in range(WWW):
        l = []
        for y in range(HHH):
            col = getColor(getPixelStep(x, y))
            l = l + [col >> 8, col & 0xff]
        LCD.ShowBuffer(x, x, 0, 319, bytearray(l))


class CooperativeDraw:
    def __init__(self):
        self.jobs = []
        self.levels = 3

    def Calc(self):
        w = WWW-1
        h = HHH-1
        self.rec(
            self.levels,
            0, w, 0, h,
            getPixelStep(0, 0), getPixelStep(w, 0),
            getPixelStep(0, h), getPixelStep(w, h))
        return False

    def storeJob(self, x1, x2, y1, y2, v11, v12, v21, v22):
        global LCD
        # print(x1, y1, v11)
        window.setLocation(x1,x2,y1,y2)
        window.fill(0xffff)
        window.render()
        # LCD.ShowPoint(x1, y1, getColor(v11))
        # LCD.ShowPoint(x1+1, y1, getColor(v11))
        # LCD.ShowPoint(x1, y1+1, getColor(v11))
        # LCD.ShowPoint(x1+1, y1+1, getColor(v11))
        self.jobs.append([x1, x2, y1, y2, v11, v12, v21, v22])

    def rec(self, level, x1, x2, y1, y2, v11, v12, v21, v22):
        if level == 0:
            self.storeJob(x1, x2, y1, y2, v11, v12, v21, v22)
            return

        global LCD
        if y1 == y2:
            window.resetBuf()
            col = getColor(v11)
            window.writeColor(col)
            x = x1+1
            while x <= x2:
                if x == x2:
                    col = getColor(v21)
                else:
                    col = getColor(getPixelStep(x, y1))
                window.writeColor(col)
                x += 1
            LCD.ShowBuffer(x1, x2, y1, y1, window.content())
            return

        if y1 == y2-1:
            self.rec(level-1, x1, x2, y1, y1, v11, v11, v21, v21)
            self.rec(level-1, x1, x2, y2, y2, v12, v12, v22, v22)
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
            n = (x2-x1+1)*(y2-y1+1)
            if n <  window.maxPixelNum:
                window.repeatColor(col, n)
                LCD.ShowBuffer(x1, x2, y1, y2, window.content())
                return

        self.rec(level-1, x1, xo, y1, yo, v11, v1o, vo1, voo)
        self.rec(level-1, x1, xo, yo, y2, v1o, v12, voo, vo2)
        self.rec(level-1, xo, x2, y1, yo, vo1, voo, v21, v2o)
        self.rec(level-1, xo, x2, yo, y2, voo, vo2, v2o, v22)

def f(b):
    b2 = b[:19360]
    b2[10000] = 1
    print(b2[10000], b[10000])

def main():
    global LCD
    LCD.BackLight(100)

    initColors()

    start = time.time()
    print('hello')
    # DrawAll()
    CooperativeDraw().Calc()
    # b = bytearray(20000)
    # f(b)

    print('total time', time.time()-start)


if __name__ == '__main__':
    main()

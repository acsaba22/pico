import liblcd
import time
import framebuf
import math
import random

def drawLine(screen, x1, x2, y1, y2, color):
#    b = bytearray(liblcd.color_to_bytes(color) * (x2-x1+1)*(y2-y1+1))
#    screen.ShowBuffer(x1, x2, y1, y2, b)
    screen.FillBuffer(x1, x2, y1, y2, color)

def drawLineOpt(screen, x1, x2, y1, y2, b):
    screen.ShowBuffer(x1, x2, y1, y2, b)


class Stamp:
    def __init__(self, s, xn, yn, color1Byte):
        self.s = s
        self.b = bytearray([color1Byte] * 2 * xn * yn)
        self.xd = xn - 1
        self.yd = yn - 1

    def show(self, x1, y1):
        self.s.ShowBuffer(x1, x1+self.xd, y1, y1+self.yd, self.b)

class Labyrinth(object):
    SIDE_N = 0
    SIDE_R = 1
    SIDE_D = 2
    SIDE_RD = 3
    ITEM_WIDTH = 10
    ITEM_HEIGHT = 10
    
    def __init__(self, screen):
        self.screen = screen
        self.lab = []
        for y in range((320//self.ITEM_HEIGHT)-1):
            self.lab.append([self.SIDE_N] * ((400//self.ITEM_WIDTH) - 1))
        self.stamps = [Stamp(screen, self.ITEM_WIDTH, self.ITEM_HEIGHT, 0),
                       Stamp(screen, self.ITEM_WIDTH, self.ITEM_HEIGHT, 0),
                       Stamp(screen, self.ITEM_WIDTH, self.ITEM_HEIGHT, 0),
                       Stamp(screen, self.ITEM_WIDTH, self.ITEM_HEIGHT, 0)]
        fb = framebuf.FrameBuffer(self.stamps[0].b, self.ITEM_WIDTH, self.ITEM_HEIGHT, framebuf.RGB565)
        fb.fill(0xFFFF)
        fb = framebuf.FrameBuffer(self.stamps[1].b, self.ITEM_WIDTH, self.ITEM_HEIGHT, framebuf.RGB565)
        fb.fill(0xFFFF)
        fb.vline(self.ITEM_WIDTH-1,0,self.ITEM_HEIGHT,0x0)
        fb = framebuf.FrameBuffer(self.stamps[2].b, self.ITEM_WIDTH, self.ITEM_HEIGHT, framebuf.RGB565)
        fb.fill(0xFFFF)
        fb.hline(0,self.ITEM_HEIGHT-1,self.ITEM_WIDTH,0x0)
        fb = framebuf.FrameBuffer(self.stamps[3].b, self.ITEM_WIDTH, self.ITEM_HEIGHT, framebuf.RGB565)
        fb.fill(0xFFFF)
        fb.vline(self.ITEM_WIDTH-1,0,self.ITEM_HEIGHT,0x0)
        fb.hline(0,self.ITEM_HEIGHT-1,self.ITEM_WIDTH,0x0)
        
#        self.lab = []
#        for y in range(5):
#            self.lab.append([self.SIDE_N] * 5)
        self.generate()
        self.algo = 0
            
    def generate(self):

        def add_vert(y1, y2, x):
            g = random.randrange(y1, y2)
            for y in range(y1, y2):
                if g != y:
                    self.lab[y][x] |= self.SIDE_R
            return x
        def add_horiz(x1, x2, y):
            g = random.randrange(x1, x2)
            for x in range(x1, x2):
                if g != x:
                    self.lab[y][x] |= self.SIDE_D
            return y
        
        def split(x, y, w, h):
            if (w <= 1) or (h <= 1):
                return
            ny = random.randrange(y, y+h-1)
            add_horiz(x, x+w, ny)
            nx1 = random.randrange(x, x+w-1)
            nx2 = random.randrange(x, x+w-1)
            add_vert(y, ny+1, nx1)
            add_vert(ny+1, y+h, nx2)
            split(x, y, nx1-x+1, ny+1-y)
            split(nx1+1, y, x+w-nx1-1, ny+1-y)
            split(x, ny+1, nx2-x+1, y+h-ny-1)
            split(nx2+1, ny+1, x+w-nx2-1, y+h-ny-1)
            

        w = len(self.lab[0])
        h = len(self.lab)
        split(0, 0, w, h)
        
    def draw(self):
       
        if self.algo == 1:
            y2 = -1
            for y in range(len(self.lab)):
                y2 += self.ITEM_HEIGHT
                x2 = -1
                b = bytearray(2*self.ITEM_WIDTH*len(self.lab[y]))
                for x in range(len(self.lab[y])):
                    x1, x2 = x2+1, x2 + self.ITEM_WIDTH
                    v = self.lab[y][x]
                    if v & self.SIDE_D:
                        pass
                    else:
                        for i in range(x1<<1, x2<<1, 2):
                            b[i] = 0xFF
                            b[i+1] = 0xFF
                self.screen.ShowBuffer(0,x2, y2, y2, b)
            x2 = -1
            for x in range(len(self.lab[0])):
                x2 += self.ITEM_WIDTH
                y2 = -1
                b = bytearray(2*self.ITEM_WIDTH*len(self.lab))
                for y in range(len(self.lab)):
                    y1, y2 = y2+1, y2 + self.ITEM_HEIGHT
                    v = self.lab[y][x]
                    if v & self.SIDE_R:
                        pass
                    else:
                        for i in range(y1<<1, y2<<1, 2):
                            b[i] = 0xFF
                            b[i+1] = 0xFF
                self.screen.ShowBuffer(x2,x2, 0, y2, b)
        if self.algo == 2:
            for y in range(len(self.lab)):
                for x in range(len(self.lab[y])):
                    self.stamps[self.lab[y][x]].show(x*self.ITEM_WIDTH, y*self.ITEM_HEIGHT)
        if self.algo == 0:
            y2 = -1
            for y in range(len(self.lab)):
                y1, y2 = y2+1, y2 + self.ITEM_HEIGHT
                x2 = -1
                for x in range(len(self.lab[y])):
                    x1, x2 = x2+1, x2 + self.ITEM_WIDTH
                    v = self.lab[y][x]
                    if v & self.SIDE_R:
                        drawLine(self.screen, x2, x2, y1, y2, liblcd.BLACK)
                    else:
                        drawLine(self.screen, x2, x2, y1, y2, liblcd.WHITE)
                    if v & self.SIDE_D:
                        drawLine(self.screen, x1, x2, y2, y2, liblcd.BLACK)
                    else:
                        drawLine(self.screen, x1, x2, y2, y2, liblcd.WHITE)
        if self.algo == 3:
            self.screen.Clear()
            y2 = -1
            for y in range(len(self.lab)):
                y1, y2 = y2+1, y2 + self.ITEM_HEIGHT
                x2 = -1
                for x in range(len(self.lab[y])):
                    x1, x2 = x2+1, x2 + self.ITEM_WIDTH
                    v = self.lab[y][x]
                    if v & self.SIDE_R:
                        drawLine(self.screen, x2, x2, y1, y2, liblcd.BLACK)
                    if v & self.SIDE_D:
                        drawLine(self.screen, x1, x2, y2, y2, liblcd.BLACK)

        x1, x2, y1, y2 = 0, self.ITEM_WIDTH*(len(self.lab[0]))-1, 0, self.ITEM_HEIGHT*(len(self.lab))-1
        drawLine(self.screen, x1, x2, y1, y1, liblcd.BLACK)
        drawLine(self.screen, x1, x2, y2, y2, liblcd.BLACK)
        drawLine(self.screen, x1, x1, y1, y2, liblcd.BLACK)
        drawLine(self.screen, x2, x2, y1, y2, liblcd.BLACK)
        y1 = self.ITEM_HEIGHT*(len(self.lab)//2)
        y2 = y1+self.ITEM_HEIGHT-1
        drawLine(self.screen, x1, x1, y1, y2, liblcd.WHITE)
        drawLine(self.screen, x2, x2, y1, y2, liblcd.WHITE)
        

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    ts = time.ticks_ms()
    screen.Clear()
    te = time.ticks_ms()
    print("Clear duration: ", time.ticks_diff(te, ts))
    redo = liblcd.Button(screen, liblcd.Box(400, 479, 260, 319))
    stop = liblcd.Button(screen, liblcd.Box(400, 479, 0, 59))
    touch = liblcd.SmartTouch(screen)

    labyrinth = Labyrinth(screen)
    algo = 2
    while True:
        screen.Clear()
        redo.draw()
        stop.draw()
        
        
        labyrinth.algo = algo
        ts = time.ticks_ms()
        labyrinth.draw()
        te = time.ticks_ms()
        print("duration: ", time.ticks_diff(te, ts))
        while True:
            t = touch.get()
            if redo.do(t):
                break
            if stop.do(t):
                algo = (algo+1)%4
                print("algo=", algo)
#                screen.Clear()
                break
                return


if __name__ == '__main__':
    main()





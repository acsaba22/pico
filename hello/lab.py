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
    SIDE_NONE = 0
    SIDE_R = 1
    SIDE_D = 2
    SIDE_RD = 3
    
    def __init__(self, screen, offset_x=0, offset_y=0, size_x=400, size_y=320, item_width=30, item_height=30):
        self.screen = screen
        self.lab = []
        self.offset_x = offset_x
        self.offset_y = offset_y
        self.ITEM_WIDTH = item_width
        self.ITEM_HEIGHT = item_height
        self.width = (size_x//self.ITEM_WIDTH)
        self.height = (size_y//self.ITEM_HEIGHT)
        for y in range(self.height):
            self.lab.append([self.SIDE_NONE] * self.width)        
        self.generate()
            
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
            nx = random.randrange(x, x+w-1)
            add_vert(y, y+h, nx)
            ny1 = random.randrange(y, y+h-1)
            ny2 = random.randrange(y, y+h-1)
            add_horiz(x, nx+1, ny1)
            add_horiz(nx+1, x+w, ny2)
            split(x, y, nx-x+1, ny1+1-y)
            split(nx+1, y, x+w-nx-1, ny2+1-y)
            split(x, ny1+1, nx-x+1, y+h-ny1-1)
            split(nx+1, ny2+1, x+w-nx-1, y+h-ny2-1)

        for y in range(self.height):
            for x in range(self.width):
                self.lab[y][x] = self.SIDE_NONE
        split(0, 0, self.width, self.height)
        
    def draw(self):       
        y2 = -1
        for y in range(self.height):
            y2 += self.ITEM_HEIGHT
            x2 = -1
            b = bytearray(2*self.ITEM_WIDTH*len(self.lab[y]))
            for x in range(self.width):
                x1, x2 = x2+1, x2 + self.ITEM_WIDTH
                v = self.lab[y][x]
                if not (v & self.SIDE_D):
                    for i in range(x1<<1, x2<<1, 2):
                        b[i] = 0xFF
                        b[i+1] = 0xFF
            self.screen.ShowBuffer(self.offset_x,x2+self.offset_x, y2+self.offset_y, y2+self.offset_y, b)
        x2 = -1
        for x in range(self.width):
            x2 += self.ITEM_WIDTH
            y2 = -1
            b = bytearray(2*self.ITEM_WIDTH*len(self.lab))
            for y in range(self.height):
                y1, y2 = y2+1, y2 + self.ITEM_HEIGHT
                v = self.lab[y][x]
                if not (v & self.SIDE_R):
                    for i in range(y1<<1, y2<<1, 2):
                        b[i] = 0xFF
                        b[i+1] = 0xFF
            self.screen.ShowBuffer(x2+self.offset_x,x2+self.offset_x, self.offset_y, y2+self.offset_y, b)

        x1, x2, y1, y2 = (self.offset_x, self.offset_x+self.ITEM_WIDTH*self.width-1,
                          self.offset_y, self.offset_y+self.ITEM_HEIGHT*self.height-1)
        drawLine(self.screen, x1, x2, y1, y1, liblcd.BLACK)
        drawLine(self.screen, x1, x2, y2, y2, liblcd.BLACK)
        drawLine(self.screen, x1, x1, y1, y2, liblcd.BLACK)
        drawLine(self.screen, x2, x2, y1, y2, liblcd.BLACK)
        y1 = self.offset_y+self.ITEM_HEIGHT*(len(self.lab)//2)
        y2 = y1+self.ITEM_HEIGHT-1
        drawLine(self.screen, x1, x1, y1, y2, liblcd.WHITE)
        drawLine(self.screen, x2, x2, y1, y2, liblcd.WHITE)
        
    def getStartPos(self):
        return (0, self.height//2)
    def isEndPos(self, pos):
        return pos == (self.width, self.height//2)
        
    def scalePos(self, pos):
        return liblcd.Coord(
            self.offset_x+pos[0]*self.ITEM_WIDTH + self.ITEM_WIDTH//2,
            self.offset_y+pos[1]*self.ITEM_HEIGHT + self.ITEM_HEIGHT//2)
    
    def isValidDir(self, pos, dx, dy):
        x, y = pos
        if (x+dx == self.width):
            return y == self.height//2
        if not (0 <= x + dx < self.width):
            return False
        if not (0 <= y + dy < self.height):
            return False
        if abs(dx) + abs(dy) > 1:
            return False
        if dx == -1:
            return not (self.lab[y][x-1] & self.SIDE_R)
        if dx == 1:
            return not (self.lab[y][x] & self.SIDE_R)
        if dy == -1:
            return not (self.lab[y-1][x] & self.SIDE_D)
        if dy == 1:
            return not (self.lab[y][x] & self.SIDE_D)
        print (pos, dx, dy)
        return False
                
            

class Player(object):
    W = 12
    H = 14
    FACE = bytearray(b'\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xf7\xff\xc5u\xc4\xb3\xcdv\xf7\xbe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xa2\xcc\xb8\x84\x99\xe8\xce\x18\xf7\xbe\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xdf<\xa8\x83\xb9&\xb3n\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xb3M\xc1&\xc1F\xa1\x87\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xef\xdfpB\x89%\x81Ex!\xef\xde\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\x9b\xaf\xff\xff\xad\xf7\xce\xba\xef]\xac\x92\xff\xff\xff\xff\xff\xff\xff\xff\xff\xdf\xbd\x94r\xc8\xde\x99\xdd\x94\xdd\xb6\xde\x98{*\xdeV\xff\xff\xff\xff\xff\xff\xef}I#\xee\x96\xcd\x93\xcc\x0e\xc3\xed\xde\x15\xde\x15Y\xe6\xf7\xff\xff\xff\xff\xff\xbd\xb6rG\xe6v\xee\xb7\xff8\xff8\xe6v\xe6\x96rg\x8b\x8d\xff\xff\xff\xff\x8b\x8dj&\xffY\xfe\xf8\xf6\xd7\xf6\xd7\xff8\xee\xd7ac\xbe\x18\xff\xff\xff\xff\xb6\x18ac\x93\x8c\xf6\xf8\xffy\xffz\xcd\xb4r&Q\xa5\xd6\xdb\xff\xff\xff\xff\xe7\x1b\x83li\xe5a\x84i\xc5a\xa4y\xe5Q\xe6\xbds\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff1\xc82\nsmsM)\xa89\xe8\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff\xd6\x9a\x94q\xbd\xd6\xff\xff\xff\xff\xbd\xb6\x94\x91\xd6\xba\xff\xff\xff\xff')
    def __init__(self, screen):
        self.sprite = liblcd.Sprite(screen, self.W, self.H)
        self.sprite.setBuffer(self.FACE)
        self.reset()

    def reset(self):
        self.sprite.hide()

    def moveTo(self, coord):
        self.sprite.move(coord)
        
    def hide(self):
        self.sprite.hide()

    def show(self):
        self.sprite.show()

class Score(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 96, 8)
        self.sprite.move(liblcd.Coord(10, 1))
        self.fb = self.sprite.getFramebuffer()
        self.reset()

    def reset(self):
        self.score = 0
        self.sprite.hide()
        self.update()

    def update(self):
        self.fb.fill(liblcd.WHITE)
        self.fb.text("score: %d" % (self.score, ), 0, 0, liblcd.BLACK)
        self.sprite.draw()

    def increase(self):
        self.score += 1
        self.update()

    def hide(self):
        self.sprite.hide()

    def show(self):
        self.sprite.show()
        
    def draw(self):
        self.sprite.draw()

def sign(x):
    if x > 0: return 1
    elif x < 0: return -1
    return 0

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    screen.Clear()
    touch = liblcd.SmartTouch(screen)

    score = Score(screen)
    player = Player(screen)
    lab_size = 50
    while True:
        screen.Clear()
        score.draw()
        player.hide()
        lab = Labyrinth(screen, offset_x=2, offset_y=15, size_x=475, size_y=300, item_width=lab_size, item_height=lab_size)
        lab.draw()
        pos = lab.getStartPos()
        player.moveTo(lab.scalePos(pos))
        player.show()
        score.show()

        touch_start = None
        while True:
            t = touch.get()
            if not touch_start and t:
                touch_start = t
            elif touch_start and t:
                dx = t[0] - touch_start[0]
                dy = t[1] - touch_start[1]
                if max(abs(dx), abs(dy)) > 20:
                    if abs(dx) > abs(dy):
                        dx, dy = sign(dx), 0
                    else:
                        dx, dy = 0, sign(dy)
                    if (dx != 0 or dy != 0) and lab.isValidDir(pos, dx, dy):
                        pos = (pos[0]+dx, pos[1]+dy)
                        player.moveTo(lab.scalePos(pos))
                        if lab.isEndPos(pos):
                            break
                    touch_start = t
            if not t:
                touch_start, last_touch = None, None
                
        score.increase()
        if lab_size > 18: lab_size -= 2


if __name__ == '__main__':
    main()





import liblcd
import os


import framebuf
import time

class Button(object):

    def __init__(self, screen, box,
                 text="",
                 color_surface=liblcd.RGB_FB(128, 128, 128),
                 color_surface_pressed=liblcd.RGB_FB(160, 160, 160),
                 color_text=liblcd.RGB_FB(0, 0, 0)):
        self._state = 0

        self.screen = screen
        self.box = liblcd.Box(int(box.x1), int(box.x2), int(box.y1), int(box.y2))

        self.text = text
        self.color_surface = color_surface
        self.color_surface_pressed = color_surface_pressed
        self.color_text = color_text
        self.draw()

    def draw(self):
        if self._state:
            self._drawPressed()
        else:
            self._drawNormal()

    def setText(self, text):
        self.text = text
        self.draw()

    def _getFB(self):
        buf = bytearray(self.box.width * self.box.height * 2)
        fb = framebuf.FrameBuffer(buf, self.box.width, self.box.height, framebuf.RGB565)
        return fb, buf

    def _drawEdge(self, fb):
        pass

    def _drawSurface(self, fb):
        if self._state:
            fb.fill_rect(0, 0, self.box.width, self.box.height, self.color_surface)
        else:
            fb.fill_rect(0, 0, self.box.width, self.box.height, self.color_surface_pressed)

    def _drawNormal(self):
        fb, buf = self._getFB()
        self._drawSurface(fb)
        self._drawEdge(fb)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4), self.box.height // 2 - 4, self.color_text)
        self.screen.ShowBufferAtBox(self.box, buf)

    def _drawPressed(self):
        fb, buf = self._getFB()
        self._drawSurface(fb)
        self._drawEdge(fb)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4)+2, self.box.height // 2 - 2, self.color_text)
        self.screen.ShowBufferAtBox(self.box, buf)

    def _setState(self, new_state):
        new_state = min(1, max(0, new_state))
        if self._state == new_state:
            return
        self._state = new_state
        self.draw()

    def do(self, touch):
        if touch != None:
            c = liblcd.Coord(touch[0], touch[1])
            if c in self.box:
                self._setState(1)
            elif self._state == 1:
                # print ("left %s" % (c, ))
                self._setState(0)
        elif self._state == 1:
            self._setState(0)
            self.doPressed()
            return True
        return False

    def doPressed(self):
        pass

class Button3D(Button):
    def __init__(self, screen, box,
                 color_edge_dark=liblcd.RGB_FB(64, 64, 64),
                 color_edge_light=liblcd.RGB_FB(192, 192, 192),
                 **kwargs):
        self.color_edge_dark = color_edge_dark
        self.color_edge_light = color_edge_light
        Button.__init__(self, screen, box, kwargs)

    def _drawUpLeftEdge(self, fb, color):
        fb.hline(0, 0, self.box.width-1, color)
        fb.hline(0, 1, self.box.width-3, color)
        fb.vline(0, 2, self.box.height-3, color)
        fb.vline(0, 3, self.box.height-5, color)

    def _drawBottomRightEdge(self, fb, color):
        fb.hline(1, self.box.height-2, self.box.width-2, color)
        fb.hline(0, self.box.height-1, self.box.width-1, color)
        fb.vline(self.box.width-2, 1, self.box.height-2, color)
        fb.vline(self.box.width-1, 0, self.box.height-1, color)

    def _drawEdge(self, fb):
        if self._state:
            self._drawBottomRightEdge(fb, self.color_edge_light)
            self._drawUpLeftEdge(fb, self.color_edge_dark)
        else:
            self._drawBottomRightEdge(fb, self.color_edge_dark)
            self._drawUpLeftEdge(fb, self.color_edge_light)

class Counter(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 96, 8)
        self.sprite.move(liblcd.Coord(10, 10))
        self.fb = self.sprite.getFramebuffer()
        self.reset()

    def reset(self):
        self.value = 0
        self.update()
        self.sprite.show()

    def update(self):
        self.fb.fill(liblcd.WHITE)
        self.fb.text("counter: %d" % (self.value, ), 0, 0, liblcd.BLACK)
        self.sprite.draw()

    def increase(self, by=1):
        self.value += by
        self.update()

    def hide(self):
        self.sprite.hide()


class Touch(object):
    def __init__(self, screen):
        self.screen = screen
        self.reads = []
        self._last_pos = None
        self._read()

    def do(self):
        self._read()

    def get(self):
        return self._last_pos

    def _read(self):
        def dist(p1, p2):
            return abs(p1[0]-p2[0])+abs(p1[1]-p2[1])
        new_time, new_pos = time.ticks_ms(), self.screen.TouchGet()
        new_value = new_time, new_pos
        has_value = 0
        self.reads = [v for v in self.reads if time.ticks_diff(new_time, v[0]) < 200 and v[1] is not None]
        if len(self.reads) < 3:
            self._last_pos = None
        elif new_pos:
            c = 0
            for v in self.reads:
                if v[1] and dist(v[1], new_pos) < 20:
                    c += 1
            if c > len(self.reads)//3:
                self._last_pos = new_pos
        if new_pos:
            self.reads.append(new_value)













LCD = liblcd.LCD_3inch5()
smartTouch = Touch(LCD)

BLACK_1_BYTE = 0x00
WHITE_1_BYTE = 0xff


def initBoard():
    b = bytearray([0xff] * 480 * 2 * 4)
    for y in range(80):
        LCD.ShowBuffer(0, 479, 4*y, 4*y+3, b)

def clearGameBoard():
    b = bytearray([0xff] * 320 * 2 * 4)
    for y in range(80):
        LCD.ShowBuffer(0, 319, 4*y, 4*y+3, b)


def Fill(x1, x2, y1, y2, color1Byte):
    b = bytearray([color1Byte] * 2 * (x2-x1+1)*(y2-y1+1))
    LCD.ShowBuffer(x1, x2, y1, y2, b)





H = 320
MAXP = 10000
MinEditZoom = 4

class Controller:
    def __init__(self):
        initBoard()
        Fill(320, 321, 0, 319, BLACK_1_BYTE)

        Fill(400, 400, 0, 319, BLACK_1_BYTE)
        Fill(320, 480, 80, 80, BLACK_1_BYTE)
        Fill(320, 480, 160, 160, BLACK_1_BYTE)
        Fill(320, 480, 240, 240, BLACK_1_BYTE)

        self.bMinus = Button(LCD, liblcd.Box(322, 399, 241, 319), text= "---")
        self.bPlus = Button(LCD, liblcd.Box(401, 479, 241, 319), text= "+++")

        self.bLoad = Button(LCD, liblcd.Box(322, 399, 161, 239), text= "LOAD")
        self.bSave = Button(LCD, liblcd.Box(401, 479, 161, 239), text= "SAVE")


        self.alive = set()

        self.setZoom(6)

        self.pushedCell = -1
        self.pushAge = 0 # TODO remove
        self.longPushCell = -1 # TODO remove

        self.viewCell = (MAXP//2)*MAXP + (MAXP//2)

        self.firstTouch = [1,2]
        self.firstTouch = None

        self.moving = False
    # def refreshBoard(self):
    #     clearGameBoard()
    #     self.DrawBoard()

    # 0..6
    # min edit 4
    def setZoom(self, zoom):
        if 0 <= zoom and zoom <= 6:
            self.zoom = zoom
            self.width = 2**self.zoom
            self.n = H / self.width
            self.drawBoard()

    def drawBoard(self):
        clearGameBoard()
        if MinEditZoom <= self.zoom:
            for i in range(self.n):
                smartTouch.do()
                k = i*self.width
                Fill(0, H-1, k, k, 0)
                Fill(k, k, 0, H-1, 0)
        for c in self.alive:
            smartTouch.do()
            self.fillCell(c, 0x00)

    def hideCells(self):
        for c in self.alive:
            smartTouch.do()
            self.fillCell(c, 0xff)

    def showCells(self):
        for c in self.alive:
            smartTouch.do()
            self.fillCell(c, 0x00)

    def Flip(self, cell):
        if cell in self.alive:
            self.alive.remove(cell)
        else:
            self.alive.add(cell)

    def findCell(self, tx, ty):
        x = tx//self.width
        y = ty//self.width
        xstart = self.viewCell//MAXP
        ystart = self.viewCell%MAXP
        x += xstart
        y += ystart
        return x*MAXP+y

    def fillCell(self, cell, color):
        x = cell//MAXP
        y = cell % MAXP

        xstart = self.viewCell//MAXP
        ystart = self.viewCell%MAXP

        x -= xstart
        y -= ystart

        if x < 0 or self.n <= x or y < 0 or self.n <= y:
            return
        sx1 = x*self.width
        sx2 = sx1 + self.width - 1
        sy1 = y*self.width
        sy2 = sy1+self.width - 1
        if MinEditZoom <= self.zoom:
            sx1+=1
            sy1+=1
        Fill(sx1,sx2,sy1,sy2,color)

    def showCell(self, cell):
        color = 0xff
        if cell in self.alive:
            color = 0x00
        self.fillCell(cell, color)

    def Save(self):
        dirs = os.listdir()
        if 'life' not in dirs:
            os.mkdir('life')
        f = open('life/002', 'w')
        f.write(repr(self.alive))

    def Load(self):
        f = open('life/002')
        s = f.read()
        print(s)
        self.alive = eval(s)
        self.drawBoard()

    def Move(self, touch):
        if not self.firstTouch:
            return
        xd = abs(touch[0]-self.firstTouch[0])
        yd = abs(touch[1]-self.firstTouch[1])
        if 100 < xd + yd or self.moving:
            nowCell = self.findCell(touch[0], touch[1])
            startCell = self.findCell(self.firstTouch[0], self.firstTouch[1])
            nextCell = self.firstViewCell + (startCell - nowCell)
            if self.viewCell != nextCell:
                self.hideCells()
                self.viewCell = nextCell
                self.showCells()
                return True
        return False


    def do(self):
        smartTouch.do()
        touch = smartTouch.get()

        if not self.firstTouch and touch:
            self.firstTouch = touch
            self.firstViewCell = self.viewCell

        # print('touch:', touch)
        if not touch:
            self.firstTouch = None
            # if self.moving:
                # print('moving stop')
            self.moving = False


        if self.bPlus.do(touch):
            print('touched +')
            self.setZoom(self.zoom+1)
        if self.bMinus.do(touch):
            print('touched -')
            self.setZoom(self.zoom-1)
        if self.bSave.do(touch):
            print('touched Save')
            self.Save()
        if self.bLoad.do(touch):
            print('touched Load')
            self.Load()

        if self.Move(touch) or self.moving:
            # print('moving start')
            self.moving = True
            return

        currentCell = -1
        if touch and MinEditZoom <= self.zoom:
            tx, ty = touch
            if tx < 320:
                currentCell = self.findCell(tx, ty)

        if self.pushedCell == currentCell:
            self.pushAge += 1
            if 5 < self.pushAge:
                self.longPushCell = self.pushedCell
        else:
            if self.pushedCell != -1:
                if currentCell == -1:
                    self.Flip(self.longPushCell)
                    self.showCell(self.longPushCell)
                self.showCell(self.pushedCell)
            self.pushedCell = currentCell
            self.fillCell(self.pushedCell, 0x55)



def main():
    LCD.BackLight(100)
    # initBoard()
    # Fill(320, 320, 0, 319, BLACK_1_BYTE)
    print('hello life')
    c = Controller()
    while True:
        c.do()
        time.sleep_us(1)


main()

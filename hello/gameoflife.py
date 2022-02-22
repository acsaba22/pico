import liblcd
import os
import time


LCD = liblcd.LCD_3inch5()
smartTouch = liblcd.SmartTouch(LCD)

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

        self.bMinus = liblcd.Button(LCD, liblcd.Box(322, 399, 241, 319), text= "---")
        self.bPlus = liblcd.Button(LCD, liblcd.Box(401, 479, 241, 319), text= "+++")

        self.bLoad = liblcd.Button(LCD, liblcd.Box(322, 399, 161, 239), text= "LOAD")
        self.bSave = liblcd.Button(LCD, liblcd.Box(401, 479, 161, 239), text= "SAVE")


        self.alive = set()

        self.setZoom(6)

        self.touchedCell = -1

        self.viewCell = (MAXP//2)*MAXP + (MAXP//2)

        self.firstTouch = [1,2]
        self.firstTouch = None

        self.moving = False

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
        self.showCells()

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

    def findCell(self, touch):
        tx, ty = touch
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
            nowCell = self.findCell(touch)
            startCell = self.findCell(self.firstTouch)
            nextCell = self.firstViewCell + (startCell - nowCell)
            if self.viewCell != nextCell:
                self.hideCells()
                self.viewCell = nextCell
                self.showCells()
                return True
        return False

    def removeTouchSelection(self):
        self.showCell(self.touchedCell)
        self.touchedCell = -1

    def flipIfReleased(self, touch):
        if not touch:
            if self.touchedCell != -1:
                self.Flip(self.touchedCell)
                self.removeTouchSelection()
            return

        currentCell = -1
        if MinEditZoom <= self.zoom and touch[0] < 320:
                currentCell = self.findCell(touch)

        if currentCell != self.touchedCell:
            self.removeTouchSelection()
            self.touchedCell = currentCell
            self.fillCell(self.touchedCell, 0x55)


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
        self.flipIfReleased(touch)



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

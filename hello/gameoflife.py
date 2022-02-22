import liblcd
import os
import time


LCD = liblcd.LCD_3inch5()
smartTouch = liblcd.SmartTouch(LCD, yCorrection=-10)

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
    # LCD.FillBuffer(x1, x2, y1, y2, bytearray([color1Byte, color1Byte ]))


class Stamp:
    def __init__(self, xn, yn, color1Byte):
        self.b = bytearray([color1Byte] * 2 * xn * yn)
        self.xd = xn - 1
        self.yd = yn - 1

    def show(self, x1, y1):
        LCD.ShowBuffer(x1, x1+self.xd, y1, y1+self.yd, self.b)


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

        self.bMinus = liblcd.Button(
            LCD, liblcd.Box(322, 399, 241, 319), text="---")
        self.bPlus = liblcd.Button(
            LCD, liblcd.Box(401, 479, 241, 319), text="+++")

        self.bLoad = liblcd.Button(
            LCD, liblcd.Box(322, 399, 161, 239), text="LOAD")
        self.bSave = liblcd.Button(
            LCD, liblcd.Box(401, 479, 161, 239), text="SAVE")

        self.alive = set()

        self.setZoom(4)

        self.touchedCell = -1

        self.cornerCell = (MAXP//2)*MAXP + (MAXP//2)

        self.firstTouch = [1, 2]
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
            drawWidth = self.width
            if 4 <= zoom:
                drawWidth -= 1
            self.stampLive = Stamp(drawWidth, drawWidth, 0x00)
            self.stampDead = Stamp(drawWidth, drawWidth, 0xff)
            self.stampMarked = Stamp(drawWidth, drawWidth, 0x55)

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
            self.fillCell(c, self.stampDead)

    def showCells(self):
        for c in self.alive:
            smartTouch.do()
            self.fillCell(c, self.stampLive)

    def Flip(self, cell):
        if cell in self.alive:
            self.alive.remove(cell)
        else:
            self.alive.add(cell)

    def findCell(self, touch):
        tx, ty = touch
        x = tx//self.width
        y = ty//self.width
        xstart = self.cornerCell//MAXP
        ystart = self.cornerCell % MAXP
        x += xstart
        y += ystart
        return x*MAXP+y

    def fillRelativeCellStamp(self, cell, stamp: Stamp):
        x = cell//MAXP
        y = cell % MAXP

        if x < 0 or self.n <= x or y < 0 or self.n <= y:
            return
        sx1 = x*self.width
        sy1 = y*self.width
        if MinEditZoom <= self.zoom:
            sx1 += 1
            sy1 += 1
        stamp.show(sx1, sy1)

    def fillCell(self, cell, stamp: Stamp):
        self.fillRelativeCellStamp(cell-self.cornerCell, stamp)

    def showCell(self, cell):
        if cell in self.alive:
            self.fillCell(cell, self.stampLive)
        else:
            self.fillCell(cell, self.stampDead)

    def Save(self):
        dirs = os.listdir()
        if 'life' not in dirs:
            os.mkdir('life')
        f = open('life/002', 'w')
        f.write(repr(self.alive))

    def Load(self):
        f = open('life/002')
        s = f.read()
        self.alive = eval(s)
        self.drawBoard()

    def visibleRelativeCellsWithCorner(self, corner):
        ret = set()
        for cell in self.alive:
            relCell = cell-corner
            if relCell//MAXP < self.n and relCell % MAXP < self.n:
                ret.add(relCell)
        return ret

    def moveCornerCell(self, newCornerCell):
        visibleCellsBefore = self.visibleRelativeCellsWithCorner(
            self.cornerCell)
        visibleCellsAfter = self.visibleRelativeCellsWithCorner(newCornerCell)
        toRemove = visibleCellsBefore - visibleCellsAfter
        toAdd = visibleCellsAfter - visibleCellsBefore

        for cell in toAdd:
            smartTouch.do()
            self.fillRelativeCellStamp(cell, self.stampLive)

        for cell in toRemove:
            smartTouch.do()
            self.fillRelativeCellStamp(cell, self.stampDead)

        self.cornerCell = newCornerCell


    def Drag(self, touch):
        if not touch:
            self.firstTouch = None
            if self.moving:
                self.moving = False
                return True
            return False

        if not self.firstTouch:
            self.firstTouch = touch
            self.firstCornerCell = self.cornerCell
            return False

        xd = abs(touch[0]-self.firstTouch[0])
        yd = abs(touch[1]-self.firstTouch[1])
        if 60 < xd + yd or self.moving:
            if not self.moving:
                self.removeTouchSelection()
                self.moving = True
            nowCell = self.findCell(touch)
            startCell = self.findCell(self.firstTouch)
            nextCornerCell = self.firstCornerCell + (startCell - nowCell)
            if self.cornerCell != nextCornerCell:
                self.moveCornerCell(nextCornerCell)
                return True
        return self.moving

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
            self.fillCell(self.touchedCell, self.stampMarked)

    def do(self):
        smartTouch.do()
        touch = smartTouch.get()

        if self.bPlus.do(touch):
            self.setZoom(self.zoom+1)
        if self.bMinus.do(touch):
            self.setZoom(self.zoom-1)
        if self.bSave.do(touch):
            self.Save()
        if self.bLoad.do(touch):
            self.Load()

        if self.Drag(touch):
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

# Banchmark:

# ts = time.ticks_ms()
# ...
# te = time.ticks_ms()
# print("duration: ", time.ticks_diff(te, ts))

import framebuf
import random
import liblcd
import os
import time
import gc
import sys

LCD = liblcd.LCD_3inch5()
smartTouch = liblcd.SmartTouch(LCD, yCorrection=-10)

BLACK_1_BYTE = 0x00
WHITE_1_BYTE = 0xff
# MyColor = 0x5555


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

FolderName = 'life'


class Layout:
    def Init(self):
        LCD.Clear()
        Fill(320, 321, 0, 319, BLACK_1_BYTE)

        Fill(400, 400, 0, 319, BLACK_1_BYTE)
        Fill(320, 480, 80, 80, BLACK_1_BYTE)
        Fill(320, 480, 160, 160, BLACK_1_BYTE)
        Fill(320, 480, 240, 240, BLACK_1_BYTE)

        self.boxes = [
            liblcd.Box(322, 399, 0, 79),
            liblcd.Box(401, 479, 0, 79),
            liblcd.Box(322, 399, 81, 159),
            liblcd.Box(401, 479, 81, 159),
            liblcd.Box(322, 399, 161, 239),
            liblcd.Box(401, 479, 161, 239),
            liblcd.Box(322, 399, 241, 319),
            liblcd.Box(401, 479, 241, 319)
        ]

    # 0..7
    def makeButton(self, boxNumber, text, callback=lambda: None):
        return liblcd.Button(LCD, self.boxes[boxNumber], text=text, callback=callback)


layout = Layout()

def UpdateLoadButton(button, fileName):
    f = open(FolderName + '/' + fileName)
    s = f.read()
    state = eval(s)

    min_x, max_x = MAXP, 0
    min_y, max_y = MAXP, 0
    for cell in state:
        x = cell//MAXP
        y = cell % MAXP
        min_x, max_x = min(x, min_x), max(x, max_x)
        min_y, max_y = min(y, min_y), max(y, max_y)
    if not state:
        min_x = 0
        min_y = 0
        max_x = 3
        max_y = 3
    w = min(16, max_x - min_x + 1)
    h = min(16, max_y - min_y + 1)
    size = max(w, h)
    step = 32//size
    real_size = size * step
    buf = bytearray([0xFF] * real_size*real_size*2)
    fb = framebuf.FrameBuffer(buf, real_size, real_size, framebuf.RGB565)
    for cell in state:
        x = cell//MAXP
        y = cell % MAXP
        fb.fill_rect((x-min_x)*step, (y-min_y) *
                        step, step, step, liblcd.BLACK)
    button.setImage(fb, real_size, real_size)


class Persistence:
    def __init__(self, saveButton):
        self.bSave = saveButton
        self._findSaveFile()
        self._setSaveButtonText()

        self.isLoading = False
        self.page = 0
        self.pageNum = -1

        self.fileButtons = []
        self.fileNames = []

    def createButtons(self):
        for i in range(6):
            self.fileButtons.append(layout.makeButton(i, ''))
        self.bPrevPage = layout.makeButton(6, '', callback=self.prevPage)
        self.bNextPage = layout.makeButton(7, '', callback=self.nextPage)

    def _findSaveFile(self):
        dirs = os.listdir()
        if FolderName not in dirs:
            os.mkdir(FolderName)
        fnames = sorted(os.listdir(FolderName))
        self.saveFileNumber = 0
        if fnames:
            lastName = fnames[-1]
            if len(lastName) < 3 or not lastName[:3].isdigit():
                print('ERROR: file name should start with number:', lastName)
                sys.exit()
            self.saveFileNumber = int(lastName[:3]) + 1

    def _saveFileName(self):
        return '{:03d}'.format(self.saveFileNumber)

    def _setSaveButtonText(self):
        self.bSave.setText('SAVE\n' + self._saveFileName())

    def Save(self, data):
        f = open(FolderName + '/' + self._saveFileName(), 'w')
        f.write(data)
        self.saveFileNumber += 1
        self._setSaveButtonText()

    def renderButtons(self):
        for i in range(6):
            idx = i+self.page*6
            if idx < len(self.fileNames):
                fName = self.fileNames[idx]
                self.fileButtons[i].setText(fName)
                UpdateLoadButton(self.fileButtons[i], fName)
            else:
                self.fileButtons[i].setText('')
                self.fileButtons[i].unsetImage()
        self.bPrevPage.setText('<<<' if 0 < self.page else '')
        self.bNextPage.setText('>>>' if self.page < self.pageNum-1 else '')

    def startLoad(self):
        self.isLoading = True
        self.fileNames = sorted(os.listdir(FolderName))
        self.pageNum = (len(self.fileNames)+5) // 6
        if not self.fileButtons:
            self.createButtons()
        self.renderButtons()

    def nextPage(self):
        if self.page < self.pageNum-1:
            self.page += 1
        self.renderButtons()

    def prevPage(self):
        if 0 < self.page:
            self.page -= 1
        self.renderButtons()

    def stopLoading(self):
        self.isLoading = False
        for i in range(6):
            self.fileButtons[i].unsetImage()
            self.fileButtons[i].setText('')

    def do(self, touch):
        if self.isLoading:
            if touch and touch[0] < 320:
                self.stopLoading()
                return 'CANCEL'
            self.bPrevPage.do(touch)
            self.bNextPage.do(touch)
            for i in range(6):
                if self.fileButtons[i].do(touch):
                    if self.fileButtons[i].text:
                        ret = self.fileButtons[i].text
                        self.stopLoading()
                        return ret
        return None

class Controller:

    def __init__(self):
        layout.Init()

        self.bStartStop = layout.makeButton(0, text=">>")
        self.bNext = layout.makeButton(1, text=">")
        self.bClearRandom = layout.makeButton(2, text="RANDOM")
        self.bReset = layout.makeButton(3, text="RESET")
        self.bLoad = layout.makeButton(4, text="LOAD")
        self.bSave = layout.makeButton(5, text="SAVE")
        self.bMinus = layout.makeButton(6, text="---")
        self.bPlus = layout.makeButton(7, text="+++")

        self.persistence = Persistence(self.bSave)

        self.alive = set()
        self.startState = set()

        self.setZoom(5)

        self.touchedCell = -1

        self.cornerCell = (MAXP//2)*MAXP + (MAXP//2)

        self.firstTouch = [1, 2]
        self.firstTouch = None

        self.moving = False
        self.playing = False
        self.lastPlayMs = time.ticks_ms()

    def resetButtonTexts(self):
        self.bStartStop.setText(">>")
        self.bNext.setText(">")
        self.setClearRandomButtonText()
        self.bReset.setText("RESET")
        self.bLoad.setText("LOAD")
        self.persistence._setSaveButtonText()
        self.bMinus.setText("---")
        self.bPlus.setText("+++")

    # 0..6
    # min edit 4
    def setZoom(self, zoom):
        if 0 <= zoom and zoom <= 6:
            self.zoom = zoom
            self.width = 2**self.zoom
            self.n = H // self.width
            drawWidth = self.width
            if 4 <= zoom:
                drawWidth -= 1
            self.stampLive = Stamp(drawWidth, drawWidth, 0x00)
            self.stampDead = Stamp(drawWidth, drawWidth, 0xff)
            self.stampMarked = Stamp(drawWidth, drawWidth, 0x55)

            self.drawBoard()

    def drawBoard(self):
        LCD.FillBuffer(0, 319, 0, 319, liblcd.WHITE)
        if MinEditZoom <= self.zoom:
            for i in range(self.n):
                smartTouch.do()
                k = i*self.width
                Fill(0, H-1, k, k, 0)
                Fill(k, k, 0, H-1, 0)
        self.showCells()

    def showCells(self):
        for c in self.alive:
            smartTouch.do()
            self.fillCell(c, self.stampLive)

    def flip(self, cell):
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

    def fillRelativeCell(self, cell, stamp: Stamp):
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
        self.fillRelativeCell(cell-self.cornerCell, stamp)

    def showCell(self, cell):
        if cell in self.alive:
            self.fillCell(cell, self.stampLive)
        else:
            self.fillCell(cell, self.stampDead)

    def saveStartState(self):
        self.startState = self.alive.copy()

    def loadFile(self, fileName):
        f = open(FolderName + '/' + fileName)
        s = f.read()
        self.alive = eval(s)

        # TODO set middle to the middle of the image
        cornerX = MAXP
        cornerY = MAXP
        for cell in self.alive:
            x = cell//MAXP
            y = cell%MAXP
            if x < cornerX:
                cornerX = x
            if y < cornerY:
                cornerY = y
        if cornerX == MAXP or cornerY == MAXP:
            cornerX = MAXP//2
            cornery = MAXP//2
        self.cornerCell = cornerX*MAXP + cornerY

        self.drawBoard()
        self.setClearRandomButtonText()
        self.saveStartState()

    def Load(self):
        self.persistence.startLoad()

    def visibleRelativeCells(self, corner, alive):
        ret = set()
        for cell in alive:
            relCell = cell-corner
            if relCell//MAXP < self.n and relCell % MAXP < self.n:
                ret.add(relCell)
        return ret

    def drawDiff(self, oldCornerCell, newCornerCell, oldAlive, newAlive):
        visibleCellsBefore = self.visibleRelativeCells(oldCornerCell, oldAlive)
        visibleCellsAfter = self.visibleRelativeCells(newCornerCell, newAlive)
        toRemove = visibleCellsBefore - visibleCellsAfter
        toAdd = visibleCellsAfter - visibleCellsBefore

        for cell in toAdd:
            smartTouch.do()
            self.fillRelativeCell(cell, self.stampLive)

        for cell in toRemove:
            smartTouch.do()
            self.fillRelativeCell(cell, self.stampDead)

    def moveCornerCell(self, newCornerCell):
        self.drawDiff(self.cornerCell, newCornerCell, self.alive, self.alive)
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
                self.flip(self.touchedCell)
                self.removeTouchSelection()
                self.setClearRandomButtonText()
                self.saveStartState()
            return

        currentCell = -1
        if MinEditZoom <= self.zoom and touch[0] < 320:
            currentCell = self.findCell(touch)

        if currentCell != self.touchedCell:
            self.removeTouchSelection()
            self.touchedCell = currentCell
            self.fillCell(self.touchedCell, self.stampMarked)

    def next(self):
        neighs = [-MAXP-1, -MAXP, -MAXP+1, -1, +1, MAXP-1, MAXP, MAXP+1]
        neighNum = {}
        for cell in self.alive:
            for d in neighs:
                cell2 = cell+d
                neighNum[cell2] = neighNum.get(cell2, 0)+1  # type: ignore

        nextGen = set()
        same = True
        for cell, k in neighNum.items():
            # # Buggy algo
            # if 2 <= k and k <= 4:
            #     nextGen.add(cell)
            #     same = False

            if cell in self.alive and 2 <= k and k <= 3:
                nextGen.add(cell)
            elif k == 3:
                nextGen.add(cell)
                same = False
        if len(nextGen) != len(self.alive):
            same = False
        self.drawDiff(self.cornerCell, self.cornerCell, self.alive, nextGen)

        gc.collect()
        self.alive = nextGen
        return not same

    def zoomOut(self):
        self.cornerCell -= (self.n//2)*MAXP + self.n//2
        self.setZoom(self.zoom-1)

    def zoomIn(self):
        self.cornerCell += (self.n//4)*MAXP + self.n//4
        self.setZoom(self.zoom+1)

    def stop(self):
        self.playing = False
        self.bStartStop.setText(">>")
        self.bStartStop.draw()

    def startStop(self):
        if self.playing:
            self.stop()
        else:
            self.playing = True
            self.bStartStop.setText("STOP")
            self.bStartStop.draw()

    def playIfStarted(self):
        if self.playing:
            ts = time.ticks_ms()
            if 500 < time.ticks_diff(ts, self.lastPlayMs):
                nextStart = time.ticks_ms()
                hasChange = not self.next()
                if 2000 < time.ticks_diff(time.ticks_ms(), nextStart):
                    self.stop()
                if hasChange:
                    self.stop()
                self.lastPlayMs = ts

    def generateRandom(self):
        k = 7
        chance = 40

        self.stop()
        self.alive = set()
        x = self.cornerCell//MAXP + self.n//2
        y = self.cornerCell % MAXP + self.n//2
        a = k//2
        b = k - a
        for xd in range(-a, b):
            for yd in range(-a, b):
                # print('random-e?', xd, yd)
                if random.randrange(100) < chance:
                    # print('igen!')
                    self.alive.add((x+xd)*MAXP+y+yd)

        self.drawBoard()

    def setClearRandomButtonText(self):
        if self.alive:
            self.bClearRandom.setText('CLEAR')
        else:
            self.bClearRandom.setText('RANDOM')

    def clearOrRandom(self):
        if self.bClearRandom.text == 'CLEAR':
            self.alive = set()
            self.drawBoard()
        else:
            self.generateRandom()
        self.setClearRandomButtonText()
        self.saveStartState()

    def reset(self):
        self.stop()
        self.alive = self.startState.copy()
        self.drawBoard()
        self.setClearRandomButtonText()

    def Save(self):
        self.persistence.Save(repr(self.alive))

    def do(self):
        touch = smartTouch.get()

        if self.persistence.isLoading:
            fName = self.persistence.do(touch)
            if fName:
                self.resetButtonTexts()
                if fName != 'CANCEL':
                    self.loadFile(fName)
            return

        if self.bPlus.do(touch):
            self.zoomIn()
        if self.bMinus.do(touch):
            self.zoomOut()
        if self.bSave.do(touch):
            self.Save()
        if self.bLoad.do(touch):
            self.Load()
        if self.bNext.do(touch):
            self.next()
        if self.bStartStop.do(touch):
            self.startStop()
        if self.bClearRandom.do(touch):
            self.clearOrRandom()
        if self.bReset.do(touch):
            self.reset()
            pass

        self.playIfStarted()

        if self.Drag(touch):
            return

        self.flipIfReleased(touch)


def main():
    LCD.BackLight(100)
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

import jobs
import timestats
from timestats import NewTimer
import plog

import asyncio
from collections import namedtuple
import gc

import liblcd
import math
import random

from collections import deque
import framebuf
import time
import os

plog.SetLevel(plog.NONE)
timestats.REPORTFREQUENCY = 180
timestats.DO_REPORT = False
TOUCH_SLEEP_REPORT_FREQ = 180 # sec



IterationStops = [20, 40, 80, 160, 240]
StartIteration = 0
ABS_LIMIT = 100

WIDTH_GOAL = 480
HEIGHT_GOAL = 320
ChunkLevel = 5
ChunkLevelMinDetail = 2
CrossPixelLength = 6
CenterDisatanceImproveRadius = 2

LCD = liblcd.LCD_3inch5()



R_FREQ = 7
G_FREQ = 11
B_FREQ = 13

R_OFFSET = 0
G_OFFSET = 0
B_OFFSET = 1.5
MIN_COLOR = 0.2

def calcColors(maxIteration):
    def color(r,g,b):
        ret = int((2**5)*r)
        ret <<= 6
        ret |= int((2**6)*g)
        ret <<= 5
        ret |= int((2**5)*b)
        return ret

    def calcColor(step):
        if step == maxIteration:
            return color(0,0,0)
        mandelColor = step
        def sinTo01(val):
            return (1-MIN_COLOR)*(val/2+0.5) + MIN_COLOR
        r = sinTo01(math.sin(mandelColor/R_FREQ + R_OFFSET))
        g = sinTo01(math.sin(mandelColor/G_FREQ + G_OFFSET))
        b = sinTo01(math.sin(mandelColor/B_FREQ + B_OFFSET))
        return color(r,g,b)


    colors = []

    for i in range(256):
        colors.append(calcColor(i))

    return colors


#===========================

ChunkSize  = 1 << ChunkLevel
ChunkSize2 = ChunkSize*ChunkSize
ChunkNumX = WIDTH_GOAL // ChunkSize
ChunkNumY = HEIGHT_GOAL // ChunkSize
WIDTH = ChunkNumX * ChunkSize
HEIGHT = ChunkNumY * ChunkSize
ChunkNum = ChunkNumX * ChunkNumY

CrossChunkX = ChunkNumX // 2
CrossChunkY = ChunkNumY // 2
CrossChunkId = CrossChunkY*ChunkNumX + CrossChunkX
CrossRedrawChunks = [
    CrossChunkId - ChunkNumX - 1,
    CrossChunkId - ChunkNumX,
    CrossChunkId - 1,
    CrossChunkId]
CrossScreenPointX = CrossChunkX * ChunkSize
CrossScreenPointY = CrossChunkY * ChunkSize

ZoomInChunkIdMapping = []
ZoomOutChunkIdMapping = []
ZoomOutDisapearSet = []
CenterOrder = []
CenterDistance = []

def calcZoomInChunkIdMapping():
    minY = -CrossChunkY
    maxY = ChunkNumY - CrossChunkY
    minX = -CrossChunkX
    maxX = ChunkNumX - CrossChunkX
    def toChunkId(y, x):
        return (y + CrossChunkY) * ChunkNumX + x + CrossChunkX
    def isValid(y, x):
        return minY <= y and y < maxY and minX <= x and x < maxX
    def validate(y, x):
        return toChunkId(y, x) if isValid(y, x) else None
    middleChunks = {}
    for y in range(minY, maxY):
        for x in range(minX, maxX):
            zy0 = 2*y
            zx0 = 2*x
            zooms = [
                validate(zy0, zx0), validate(zy0, zx0+1), 
                validate(zy0+1, zx0), validate(zy0+1, zx0+1)]
            manhatten = max(abs(y*2+1), abs(x*2+1)) // 2
            middleChunks[(manhatten, toChunkId(y, x))] = zooms

    toBool = lambda v: [x is not None for x in v]

    global ZoomInChunkIdMapping
    global ZoomOutChunkIdMapping
    global ZoomOutDisapearSet
    global CenterOrder
    
    ZoomInChunkIdMapping = []
    ZoomOutChunkIdMapping = []
    ZoomOutDisapearSet = []
    zoomOutKept = set()
    for (d, chunkId) in reversed(sorted(middleChunks)):
        mappings = middleChunks[(d, chunkId)]
        if any(toBool(mappings)):
            ZoomInChunkIdMapping.append((chunkId, mappings))

    for (d, chunkId) in sorted(middleChunks):
        CenterOrder.append(chunkId)
        CenterDistance.append(d)
        mappings = middleChunks[(d, chunkId)]
        if all(toBool(mappings)):
            ZoomOutChunkIdMapping.append((chunkId, middleChunks[(d, chunkId)]))
            zoomOutKept.add(chunkId)

    for chunkId in range(ChunkNum):
        if chunkId not in zoomOutKept:
            ZoomOutDisapearSet.append(chunkId)

calcZoomInChunkIdMapping()

def calcCrossBuffer():
    l = (CrossPixelLength*2*2*2) # up+down, 2 pixel wide, 2 byte self.clor
    ret = bytearray(b'\xff' * l)
    # for i in range(CrossPixelLength*2*2):
    #     off = 1 if i < (l//4) else 0
    #     if i % 2 == off:
    #         ret[2*i] = 0
    #         ret[2*i+1] = 0
    return ret

CrossBuffer = calcCrossBuffer()

CrossVertical = [
    CrossScreenPointX-1, CrossScreenPointX,
    CrossScreenPointY - CrossPixelLength, CrossScreenPointY + CrossPixelLength-1,
    CrossBuffer]
CrossHorizontal = [
    CrossScreenPointX - CrossPixelLength, CrossScreenPointX + CrossPixelLength-1,
    CrossScreenPointY - 1, CrossScreenPointY,
    CrossBuffer]

def RedrawCross():
    LCD.ShowBuffer(*CrossVertical)
    LCD.ShowBuffer(*CrossHorizontal)

def reportMemory():
    gc.collect()
    plog.info(f"Memory: free {gc.mem_free()//1000}k ; used {gc.mem_alloc()}k")


Point = namedtuple('Point', ['x','y'])
Interval = namedtuple('Interval', ['min', 'max'])
Square = namedtuple('Square', ['mid', 'reach'])
Rectangle = namedtuple('Rectangle', ['xi', 'yi']) # xinterval, yinterval

def PointAdd(p1, p2):
    return Point(p1.x + p2.x, p1.y + p2.y)

ChunkTotalTimer = NewTimer('ChunkTotal')
CalculateTimer = NewTimer('Calculate', ChunkTotalTimer)
DrawTimer = NewTimer('Draw', ChunkTotalTimer)
LCDShowTimer = NewTimer('LcdShow', DrawTimer)
MandelTimer = NewTimer('Mandel', CalculateTimer)

def mandelbrot(x, y, maxIteration):
    with MandelTimer:
        c = complex(x, y)
        z = complex(0, 0)
        step = 0
        while step < maxIteration and abs(z) < ABS_LIMIT:
            step += 1
            z = z*z + c
        return step

class DrawJob():
    def __init__(self) -> None:
        plog.info(f"Interactive Mandel ChunkSize: {ChunkSize} ChunkNum: {ChunkNumX} * {ChunkNumY}")
        global LCD
        LCD.BackLight(50)
        self.iterationPointer = 0
        self.resetIteration()
        self.viewportCenter = Point(-0.5, 0.0)
        self.viewPortWidth = 3.0
        self.calcViewport()

        self.valBuf = bytearray(ChunkSize2*ChunkNum)
        self.zoomBuff4x = bytearray(ChunkSize2*4)
        self.chunkColorBuf = bytearray(ChunkSize2*2)
        self.chunkLevel = [-1]*ChunkNum

        self.minLevel = -1
        self.nextChunkInOrder = 0

        reportMemory()

    def resetIteration(self):
        self.maxIteration = IterationStops[self.iterationPointer]
        plog.info(f"maxIteration {self.maxIteration}")
        self.colors = calcColors(self.maxIteration)
        self.chunkLevel = [-1]*ChunkNum
    
    def calcViewport(self):
        # instead of total viewport we use the even number of chunks around the cross
        # cross is the center like this
        cChunkNumY = CrossChunkY*2
        cChunkNumX = CrossChunkX*2
        halfWidth = self.viewPortWidth / 2
        halfHeight = cChunkNumY * halfWidth  / cChunkNumX
        center = self.viewportCenter
        xi = Interval(center.x - halfWidth, center.x + halfWidth)
        yi = Interval(center.y - halfHeight, center.y + halfHeight)
        
        self.viewPort = Rectangle(xi, yi)
        plog.info(f"Viewport: {self.viewPort}")

        chunkWidth = (xi.max - xi.min) / cChunkNumX
        self.chunkWidth = chunkWidth

        self.chunkPos = []
        ymid = yi.min

        for ky in range(ChunkNumY):
            xmid = xi.min
            for kx in range(ChunkNumX):
                self.chunkPos.append(Point(xmid, ymid))
                xmid += chunkWidth
            ymid += chunkWidth

    def drawChunk(self, chunkId):
        offset = chunkId*ChunkSize2
        screenY = (chunkId // ChunkNumX) * ChunkSize
        screenX = (chunkId % ChunkNumX) * ChunkSize
        with DrawTimer:
            bufPos = 0
            buf = self.chunkColorBuf
            valBuf = self.valBuf
            colors = self.colors
            for i in range(offset, offset + ChunkSize2):
                color = colors[valBuf[i]]
                buf[bufPos] = color >> 8
                buf[bufPos+1] = color & 0xff
                bufPos += + 2

            with LCDShowTimer:
                LCD.ShowBuffer(screenX, screenX+ChunkSize-1, screenY, screenY+ChunkSize-1, buf)

                if chunkId in CrossRedrawChunks:
                    RedrawCross()


    async def improveChunk(self, chunkId, targetLevel):
        with ChunkTotalTimer:
            with CalculateTimer:
                yieldTimer = timestats.YieldTimer(MAX_TOUCH_SLEEP_MS // 2)
                offset = chunkId*ChunkSize2
                (x0, y0) = self.chunkPos[chunkId]
                n = 1 << targetLevel
                boxSize = ChunkSize >> targetLevel
                smallWidth = self.chunkWidth / n
                smallReach = smallWidth / 2
                y = y0 + smallReach
                valBuf = self.valBuf
                maxIteration = self.maxIteration
                for by in range(offset, offset + ChunkSize2, ChunkSize*boxSize):
                    x = x0 + smallReach
                    for  bx in range (by, by+ChunkSize, boxSize):
                        mandVal = mandelbrot(x, y, maxIteration)
                        for by2 in range(bx, bx + boxSize*ChunkSize, ChunkSize):
                            for bx2 in range(by2, by2 + boxSize):
                                valBuf[bx2] = mandVal
                        await yieldTimer.yieldIfTimeout()
                        x += smallWidth
                    y += smallWidth

            await asyncio.sleep_ms(0)
            self.drawChunk(chunkId)
            await asyncio.sleep_ms(0)
            self.chunkLevel[chunkId] = targetLevel

    async def improveOneChunk(self):
        if self.minLevel == -1:
            self.minLevel = max(min(self.chunkLevel), ChunkLevelMinDetail-1, )

        if ChunkNum <= self.nextChunkInOrder:
            self.nextChunkInOrder = 0
            if ChunkLevel <= self.minLevel:
                # all done
                if random.randint(0, 100) == 0:
                    plog.info("all done")
                await asyncio.sleep_ms(10)
            else:
                self.minLevel = min(self.chunkLevel)

        centerDist = CenterDistance[self.nextChunkInOrder]
        nextChunkId = CenterOrder[self.nextChunkInOrder]

        centerAddLevel = max(0, CenterDisatanceImproveRadius - centerDist)
        goalLevel = self.minLevel + 1 + centerAddLevel
        goalLevel = max(goalLevel, ChunkLevelMinDetail)
        goalLevel = min(goalLevel, ChunkLevel)

        chunkLevel = self.chunkLevel[nextChunkId]
        if chunkLevel < goalLevel:
            await self.improveChunk(nextChunkId, goalLevel)
            await asyncio.sleep_ms(0)
        self.nextChunkInOrder += 1

    def copyChunk(self, ChunkIdFrom, ChunkIdTo):
        offsetFrom = ChunkIdFrom*ChunkSize2
        offsetTo = ChunkIdTo*ChunkSize2
        for i in range(ChunkSize2):
            self.valBuf[offsetTo+i] = self.valBuf[offsetFrom+i]
        self.chunkLevel[ChunkIdTo] = self.chunkLevel[ChunkIdFrom]

    # takes chunks and copies a doublesize in zoomBuff4x
    def zoomInBuff(self, chunkId, inverse = False):
        offset = chunkId * ChunkSize2
        valBuf = self.valBuf
        zoomBuff = self.zoomBuff4x
        for y in range(ChunkSize):
            zoomY = y*ChunkSize*4
            for x in range(ChunkSize):
                if not inverse:
                    val = valBuf[offset + y*ChunkSize+x]
                    zoomCoor = zoomY + x*2
                    zoomBuff[zoomCoor] = val
                    zoomBuff[zoomCoor+1] = val
                    zoomCoor += ChunkSize*2
                    zoomBuff[zoomCoor] = val
                    zoomBuff[zoomCoor+1] = val
                else:
                    val = 0
                    zoomCoor = zoomY + x*2
                    val += zoomBuff[zoomCoor]
                    val += zoomBuff[zoomCoor+1]
                    zoomCoor += ChunkSize*2
                    val += zoomBuff[zoomCoor]
                    val += zoomBuff[zoomCoor+1]
                    valBuf[offset + y*ChunkSize+x] = val // 4

    def zoomInCopyQuadrant(self, chunkTo, offsetBuf4, inverse = False):
        if chunkTo == None:
            return
        dest = chunkTo*ChunkSize2
        source = offsetBuf4
        zoomBuff4x = self.zoomBuff4x
        valBuf = self.valBuf
        for y in range(ChunkSize):
            for x in range(ChunkSize):
                if not inverse:
                    val = zoomBuff4x[source]
                    valBuf[dest] = val
                else:
                    val = valBuf[dest]
                    zoomBuff4x[source] = val
                dest += 1
                source += 1
            source += ChunkSize


    async def zoomIn(self):
        self.viewPortWidth /= 2
        self.calcViewport()
        plog.info(f"zoomin Start")
        offsets = [0, ChunkSize, ChunkSize2*2, ChunkSize2*2+ChunkSize]
        for chunkFrom, chunksTo in ZoomInChunkIdMapping:
            await asyncio.sleep_ms(0)
            origLevel = self.chunkLevel[chunkFrom]
            newLevel = origLevel - 1
            self.zoomInBuff(chunkFrom)
            for i, chunkTo in enumerate(chunksTo):
                if chunkTo != None:
                    self.chunkLevel[chunkTo] = newLevel

                    self.zoomInCopyQuadrant(chunkTo, offsets[i])
                    await asyncio.sleep_ms(0)

                    # self.fillChunkTest(chunkTo, 20)
                    self.drawChunk(chunkTo)

                    await asyncio.sleep_ms(0)
        plog.info(f"zoomin Finished")


    async def zoomOut(self):
        self.viewPortWidth *= 2
        self.calcViewport()
        plog.info(f"zoomout Start")
        offsets = [0, ChunkSize, ChunkSize2*2, ChunkSize2*2+ChunkSize]
        for chunkTo, chunksFrom in ZoomOutChunkIdMapping:
            minChunkLevel = ChunkLevel
            for i, chunkFrom in enumerate(chunksFrom):
                minChunkLevel = min(minChunkLevel, self.chunkLevel[chunkFrom])
                self.zoomInCopyQuadrant(chunkFrom, offsets[i], inverse = True)
            await asyncio.sleep_ms(0)

            self.zoomInBuff(chunkTo, inverse = True)
            await asyncio.sleep_ms(0)
            self.drawChunk(chunkTo)
            await asyncio.sleep_ms(0)
            self.chunkLevel[chunkTo] = min(minChunkLevel + 1, ChunkLevel-1)
        for chunkId in ZoomOutDisapearSet:
            self.chunkLevel[chunkId] = -1
        plog.info(f"zoomout Finished")

    async def doCommand(self, command):
        async def shift(vdx, vdy, rangeY, rangeX, idFromDiff):
            oldCenter = self.viewportCenter
            self.viewportCenter = Point(
                oldCenter.x + vdx * self.chunkWidth, oldCenter.y + self.chunkWidth * vdy)
            self.calcViewport()

            for cy in rangeY:
                for cx in rangeX:
                    chunkId = cy*ChunkNumX + cx
                    self.copyChunk(chunkId + idFromDiff, chunkId)
                    self.drawChunk(chunkId)
                    await asyncio.sleep_ms(0)

        if command == COMMAND_LEFT:
            await shift(-1, 0, list(range(ChunkNumY)), list(reversed(range(1, ChunkNumX))), -1)
            for cy in range(ChunkNumY):
                self.chunkLevel[cy*ChunkNumX + 0] = -1
        elif command == COMMAND_RIGHT:
            await shift(+1, 0, list(range(ChunkNumY)), list(range(0, ChunkNumX-1)), +1)
            for cy in range(ChunkNumY):
                self.chunkLevel[cy*ChunkNumX + ChunkNumX-1] = -1
        elif command == COMMAND_UP:
            await shift(0, -1, list(reversed(range(1, ChunkNumY))), list(range(1, ChunkNumX)), -ChunkNumX)
            for cx in range(ChunkNumX):
                self.chunkLevel[0 + cx] = -1
        elif command == COMMAND_DOWN:
            await shift(0, +1, list(range(0, ChunkNumY-1)), list(range(ChunkNumX)), +ChunkNumX)
            for cx in range(ChunkNumX):
                self.chunkLevel[(ChunkNumY-1)*ChunkNumX + cx] = -1
        elif command == COMMAND_ZOOM_IN:
            await self.zoomIn()
        elif command == COMMAND_ZOOM_OUT:
            await self.zoomOut()
        elif command == COMMAND_ITERATION_INC:
            if not (self.iterationPointer < len(IterationStops) - 1):
                return
            self.iterationPointer += 1
            self.resetIteration()
        elif command == COMMAND_ITERATION_DEC:
            if not(0 < self.iterationPointer):
                return
            self.iterationPointer -= 1
            self.resetIteration()
        else:
            plog.info(f"Unkown command {command}")

        self.minLevel = -1
        self.nextChunkInOrder = 0

    async def run(self):
        while True:
            command = touchControl.getCommand()
            if command != None:
                await self.doCommand(command)
            else:
                await self.improveOneChunk()
            await asyncio.sleep_ms(0)

    def fillChunkTest(self, chunkId, value):
        for x in range(chunkId*ChunkSize2, chunkId*ChunkSize2 + ChunkSize2):
            self.valBuf[x] = value


    async def checkColors(self):
        for chunkId in range(ChunkNum):
            self.fillChunkTest(chunkId, chunkId)
            self.drawChunk(chunkId)
        timestats.stats.report()
        jobs.STOP.set()


COMMAND_UP = 0
COMMAND_DOWN = 1
COMMAND_LEFT = 2
COMMAND_RIGHT = 3
COMMAND_ZOOM_IN = 4
COMMAND_ZOOM_OUT = 5
COMMAND_ITERATION_INC = 6
COMMAND_ITERATION_DEC = 7

COMMAND_STR = [
    "up", "down", "left", "right", "zoom_in", "zoom_out", "iteration_inc", "iteration_dec"]

MAX_TOUCH_SLEEP_MS = 50 # ms

class TouchControl:
    def __init__(self):
        self.touch = liblcd.SmartTouch(LCD)
        self.lastTouch = None
        self.sleepHistogram = [0] * 50
        self.lastCallMs = None
        self.commands = deque((), 100)

        self.MAX_TOUCH_SLEEP_MS = 50 # ms
        self.TOUCH_SLEEP_REPORT_FREQ = 10 # sec

    def checkSleepTime(self):
        now = time.ticks_ms()
        if self.lastCallMs != None:
            diff = time.ticks_diff(now, self.lastCallMs)
            if MAX_TOUCH_SLEEP_MS <= diff:
                plog.info(f"Warning touch time: {diff}")
            else:
                self.sleepHistogram[diff] += 1
        self.lastCallMs = now

    async def _reportSleepTimes(self):
        while True:
            await asyncio.sleep(TOUCH_SLEEP_REPORT_FREQ)
            plog.deb(f"Touch update histogram: {self.sleepHistogram}")

    def getCommand(self):
        if 0 < len(self.commands):
            return self.commands.popleft()
        return None

    async def _run(self):
        while True:
            self.checkSleepTime()
            t = self.touch.get()
            if t == None and self.lastTouch != None:
                x = self.lastTouch[0]
                y = self.lastTouch[1]
                xthird = x*3 // (WIDTH+1)
                ythird = y*3 // (HEIGHT+1)
                command = None
                if ythird == 0:
                    if xthird == 0:
                        command = COMMAND_ITERATION_INC
                    elif xthird == 1:
                        command = COMMAND_UP
                    elif xthird == 2:
                        command = COMMAND_ZOOM_IN
                elif ythird == 1:
                    if xthird == 0:
                        command = COMMAND_LEFT
                    elif xthird == 2:
                        command = COMMAND_RIGHT
                elif ythird == 2:
                    if xthird == 0:
                        command = COMMAND_ITERATION_DEC
                    elif xthird == 1:
                        command = COMMAND_DOWN
                    elif xthird == 2:
                        command = COMMAND_ZOOM_OUT
                plog.info(
                    f"Touch: {self.lastTouch}, command: {
                        COMMAND_STR[command] if command != None else "None" }")
                self.commands.append(command)
            self.lastTouch = t
            await asyncio.sleep_ms(10)

    async def start(self):
        jobs.start(self._run())
        jobs.start(self._reportSleepTimes())
        

touchControl = TouchControl()

async def main():
    jobs.start(timestats.stats.run())
    jobs.start(DrawJob().run())
    jobs.start(touchControl.start())
    # jobs.start(DrawJob().checkColors())
    await jobs.STOP.wait()

if __name__ == '__main__':
    jobs.runMain(main())

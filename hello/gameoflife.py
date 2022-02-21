import liblcd

LCD = liblcd.LCD_3inch5()
BLACK_1_BYTE = 0x00
WHITE_1_BYTE = 0xff


def initBoard():
    b = bytearray([0xff] * 480 * 2 * 4)
    for y in range(80):
        LCD.ShowBuffer(0, 479, 4*y, 4*y+3, b)


def Fill(x1, x2, y1, y2, color1Byte):
    b = bytearray([color1Byte] * 2 * (x2-x1+1)*(y2-y1+1))
    LCD.ShowBuffer(x1, x2, y1, y2, b)


H = 320
MAXP = 10000


class Controller:
    def __init__(self):
        initBoard()
        Fill(320, 322, 0, 319, BLACK_1_BYTE)

        buttons = [[323, 399, ]]

        Fill(400, 400, 0, 319, BLACK_1_BYTE)
        Fill(320, 480, 80, 80, BLACK_1_BYTE)
        Fill(320, 480, 160, 160, BLACK_1_BYTE)
        Fill(320, 480, 240, 240, BLACK_1_BYTE)

        # 0..6
        # min edit 4
        self.zoom = 6
        self.width = 2**self.zoom
        self.n = H / self.width

        self.alive = set()
        self.DrawBoard()

        self.pushedCell = -1
        self.pushAge = 0
        self.longPushCell = -1

    def DrawBoard(self):
        for i in range(self.n):
            k = i*self.width
            Fill(0, H-1, k, k, 0)
            Fill(k, k, 0, H-1, 0)

    def Flip(self, cell):
        if cell in self.alive:
            self.alive.remove(cell)
        else:
            self.alive.add(cell)

    def findCell(self, tx, ty):
        x = tx//self.width
        y = ty//self.width
        return x*MAXP+y

    def fillCell(self, cell, color):
        x = cell//MAXP
        y = cell % MAXP
        sx1 = x*self.width + 1
        sx2 = sx1 + self.width - 2
        sy1 = y*self.width + 1
        sy2 = sy1+self.width - 2
        Fill(sx1,sx2,sy1,sy2,color)

    def showCell(self, cell):
        color = 0xff
        if cell in self.alive:
            color = 0x00
        self.fillCell(cell, color)

    def Do(self):
        touch = LCD.TouchGet()
        currentCell = -1
        if touch:
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
        c.Do()


main()

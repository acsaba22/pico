
import math
from machine import Pin, SPI, PWM

import framebuf
import time
import os

LCD_DC = 8
LCD_CS = 9
LCD_SCK = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL = 13
LCD_RST = 15
TP_CS = 16
TP_IRQ = 17


class LCD_3inch5(framebuf.FrameBuffer):

    def __init__(self):
        self.RED = 0x07E0
        self.GREEN = 0x001f
        self.BLUE = 0xf800
        self.WHITE = 0xffff
        self.BLACK = 0x0000

        self.width = 480
        self.height = 1

        self.cs = Pin(LCD_CS, Pin.OUT)
        self.rst = Pin(LCD_RST, Pin.OUT)
        self.dc = Pin(LCD_DC, Pin.OUT)

        self.tp_cs = Pin(TP_CS, Pin.OUT)
        self.irq = Pin(TP_IRQ, Pin.IN)

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK),
                       mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))

        self.buffer = bytearray(self.height * self.width * 2)
        super().__init__(self.buffer, self.width, self.height, framebuf.RGB565)
        self.init_display()

    def write_cmd(self, cmd):
        self.cs(1)
        self.dc(0)
        self.cs(0)
        self.spi.write(bytearray([cmd]))
        self.cs(1)

    def write_data(self, buf):
        self.cs(1)
        self.dc(1)
        self.cs(0)
        # self.spi.write(bytearray([0X00]))
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def init_display(self):
        """Initialize dispaly"""
        self.rst(1)
        time.sleep_ms(5)
        self.rst(0)
        time.sleep_ms(10)
        self.rst(1)
        time.sleep_ms(5)
        self.write_cmd(0x21)
        self.write_cmd(0xC2)
        self.write_data(0x33)
        self.write_cmd(0XC5)
        self.write_data(0x00)
        self.write_data(0x1e)
        self.write_data(0x80)
        self.write_cmd(0xB1)
        self.write_data(0xB0)
        self.write_cmd(0x36)
        self.write_data(0x28)
        self.write_cmd(0XE0)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x04)
        self.write_data(0x0F)
        self.write_data(0x06)
        self.write_data(0x3a)
        self.write_data(0x56)
        self.write_data(0x4d)
        self.write_data(0x03)
        self.write_data(0x0a)
        self.write_data(0x06)
        self.write_data(0x30)
        self.write_data(0x3e)
        self.write_data(0x0f)
        self.write_cmd(0XE1)
        self.write_data(0x00)
        self.write_data(0x13)
        self.write_data(0x18)
        self.write_data(0x01)
        self.write_data(0x11)
        self.write_data(0x06)
        self.write_data(0x38)
        self.write_data(0x34)
        self.write_data(0x4d)
        self.write_data(0x06)
        self.write_data(0x0d)
        self.write_data(0x0b)
        self.write_data(0x31)
        self.write_data(0x37)
        self.write_data(0x0f)
        self.write_cmd(0X3A)
        self.write_data(0x55)
        self.write_cmd(0x11)
        time.sleep_ms(120)
        self.write_cmd(0x29)

        self.write_cmd(0xB6)
        self.write_data(0x00)
        self.write_data(0x62)

        self.write_cmd(0x36)
        self.write_data(0x28)

    def bl_ctrl(self, duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty >= 100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

    def draw_point(self, x, y, color):
        self.write_cmd(0x2A)

        self.write_data(x >> 8)
        self.write_data(x & 0xff)
        self.write_data(x >> 8)
        self.write_data(x & 0xff)

        self.write_cmd(0x2B)
        self.write_data(y >> 8)
        self.write_data(y & 0xff)
        self.write_data(y >> 8)
        self.write_data(y & 0xff)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        spi_color = bytearray([color >> 8, color & 0xff])
        self.spi.write(spi_color)
        self.cs(1)

    def draw_rect(self, x0, x1, y0, y1, bs):
        self.write_cmd(0x2A)

        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xff)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xff)

        self.write_cmd(0x2B)
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xff)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xff)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bs)
        self.cs(1)

    def touch_get(self):
        if self.irq() == 0:
            self.spi = SPI(1, 5_000_000, sck=Pin(LCD_SCK),
                           mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0, 3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                Y_Point = Y_Point+(((Read_date[0] << 8)+Read_date[1]) >> 3)

                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                X_Point = X_Point+(((Read_date[0] << 8)+Read_date[1]) >> 3)

            X_Point = X_Point/3
            Y_Point = Y_Point/3

            self.tp_cs(1)
            self.spi = SPI(1, 60_000_000, sck=Pin(LCD_SCK),
                           mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
            X_Point = min(480, max(0, int((X_Point-430)*480/3270)))
            Y_Point = min(320, max(0, 320-int((Y_Point-430)*320/3270)))
            Result_list = [X_Point, Y_Point]
            # print(Result_list)
            return(Result_list)


MAX_ITERATION = 100
ABS_LIMIT = 100

rFreq = 3
gFreq = 5
bFreq = 8


def calcColor(step):
    mandelColor = step / MAX_ITERATION
    r = math.sin(rFreq*mandelColor)/2+0.5
    g = math.sin(gFreq*mandelColor)/2+0.5
    b = math.sin(bFreq*mandelColor)/2+0.5
    ret = int((2**5)*r)
    ret <<= 5
    ret |= int((2**5)*b)
    ret <<= 6
    ret |= int((2**6)*g)
    return ret


colors = []


def initColors():
    # colors = []
    for i in range(MAX_ITERATION+1):
        colors.append(calcColor(i))


def color(step):
    return colors[step]


def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z**2 + c
    return step


def getPixelStep(x, y):
    return mandelbrot((x/480-0.5)*4.8, (y/320-0.5)*3.2)


maxn = 10000
buf = bytearray(maxn*2)
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
    # print('draw', x1, x2, y1, y2)
    global LCD
    if y1 == y2:
        resetBuf()
        col = color(v11)
        writeColor(col)
        x = x1+1
        while x <= x2:
            if x == x2:
                col = color(v21)
            else:
                col = color(getPixelStep(x, y1))
            writeColor(col)
            x += 1
        LCD.draw_rect(x1, x2, y1, y1, buf[:bufPos])
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
        col = color(v11)
        repeatColor(col, (x2-x1+1)*(y2-y1+1))
        LCD.draw_rect(x1, x2, y1, y2, buf[:bufPos])
        return

    DrawRec(x1, xo, y1, yo, v11, v1o, vo1, voo)
    DrawRec(x1, xo, yo, y2, v1o, v12, voo, vo2)
    DrawRec(xo, x2, y1, yo, vo1, voo, v21, v2o)
    DrawRec(xo, x2, yo, y2, voo, vo2, v2o, v22)


WWW = 480//2
HHH = 320//2


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
            col = color(getPixelStep(x, y))
            l = l + [col >> 8, col & 0xff]
        LCD.draw_rect(x, x, 0, 319, bytearray(l))


LCD = 0


def main():
    global LCD
    LCD = LCD_3inch5()
    LCD.bl_ctrl(100)

    initColors()

    start = time.time()
    print('hello')
    DrawAll()
    # DrawSlow()
    # for x in range(W):
    #     l = []
    #     # spi_color = bytearray([color>>8, color&0xff])
    #     for y in range(H):
    #         col = color(getPixelStep(x, y))
    #         l = l + [col >> 8, col & 0xff]
    #     LCD.draw_rect(x, x, 0, 319, bytearray(l))
    #     print(x, (time.time()-start)/(x+1))

    print('total time', time.time()-start)

    # color = 0xFF00
    # last_pos = None
    # while True:
    #     get = LCD.touch_get()
    #     if get != None and get != last_pos:
    #         LCD.draw_point(get[0], get[1], mandelbrot(get[0]/480, get[1]/320))
    # color += 1
    # color &= 0xFFFF
#        time.sleep(0.001)


if __name__ == '__main__':
    main()

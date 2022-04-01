
from machine import Pin,SPI,PWM

import framebuf
import time
import os

LCD_DC   = 8
LCD_CS   = 9
LCD_SCK  = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL   = 13
LCD_RST  = 15
TP_CS    = 16
TP_IRQ   = 17

class LCD_3inch5(framebuf.FrameBuffer):

    def __init__(self):
        self.RED   =   0x07E0
        self.GREEN =   0x001f
        self.BLUE  =   0xf800
        self.WHITE =   0xffff
        self.BLACK =   0x0000

        self.width = 480
        self.height = 160

        self.cs = Pin(LCD_CS,Pin.OUT)
        self.rst = Pin(LCD_RST,Pin.OUT)
        self.dc = Pin(LCD_DC,Pin.OUT)

        self.tp_cs =Pin(TP_CS,Pin.OUT)
        self.irq = Pin(TP_IRQ,Pin.IN)

        self.cs(1)
        self.dc(1)
        self.rst(1)
        self.tp_cs(1)
        self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))

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
        #self.spi.write(bytearray([0X00]))
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

    def bl_ctrl(self,duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty>=100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

    def draw_point(self,x,y,color):
        self.write_cmd(0x2A)

        self.write_data(x>>8)
        self.write_data(x&0xff)
        self.write_data(x>>8)
        self.write_data(x&0xff)

        self.write_cmd(0x2B)
        self.write_data(y>>8)
        self.write_data(y&0xff)
        self.write_data(y>>8)
        self.write_data(y&0xff)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        spi_color = bytearray([color>>8, color&0xff])
        self.spi.write(spi_color)
        self.cs(1)

    def draw_rect(self,x0,x1,y0,y1,bs):
        self.write_cmd(0x2A)

        self.write_data(x0>>8)
        self.write_data(x0&0xff)
        self.write_data(x1>>8)
        self.write_data(x1&0xff)

        self.write_cmd(0x2B)
        self.write_data(y0>>8)
        self.write_data(y0&0xff)
        self.write_data(y1>>8)
        self.write_data(y1&0xff)

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(bs)
        self.cs(1)


    def touch_get(self):
        if self.irq() == 0:
            self.spi = SPI(1,5_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            self.tp_cs(0)
            X_Point = 0
            Y_Point = 0
            for i in range(0,3):
                self.spi.write(bytearray([0XD0]))
                Read_date = self.spi.read(2)
                time.sleep_us(10)
                Y_Point=Y_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

                self.spi.write(bytearray([0X90]))
                Read_date = self.spi.read(2)
                X_Point=X_Point+(((Read_date[0]<<8)+Read_date[1])>>3)

            X_Point=X_Point/3
            Y_Point=Y_Point/3

            self.tp_cs(1)
            self.spi = SPI(1,60_000_000,sck=Pin(LCD_SCK),mosi=Pin(LCD_MOSI),miso=Pin(LCD_MISO))
            X_Point = min(480, max(0, int((X_Point-430)*480/3270)))
            Y_Point = min(320, max(0, 320-int((Y_Point-430)*320/3270)))
            Result_list = [X_Point,Y_Point]
            #print(Result_list)
            return(Result_list)

import math

MAX_ITERATION = 100
ABS_LIMIT = 100

rFreq = 3
gFreq = 5
bFreq = 8

def color(mandelColor):
  r = math.sin(rFreq*mandelColor)/2+0.5
  g = math.sin(gFreq*mandelColor)/2+0.5
  b = math.sin(bFreq*mandelColor)/2+0.5
  ret = int((2**5)*r)
  ret <<= 5
  ret |= int((2**5)*b)
  ret <<= 6
  ret |= int((2**6)*b)
  return ret

def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z**2 + c
    return color(step/MAX_ITERATION)



if __name__=='__main__':

    LCD = LCD_3inch5()
    LCD.bl_ctrl(100)

    # for x in range(480):
    #   print(x)
    #   for y in range(320):
    #     LCD.draw_point(x, y, mandelbrot((x/480-0.5)*2, (y/320-0.5)*2))

    print('hello')

    for x in range(480):
      l = []
      # spi_color = bytearray([color>>8, color&0xff])
      for y in range(320):
        col =  mandelbrot((x/480-0.5)*4.8, (y/320-0.5)*3.2)
        l = l + [col>>8, col&0xff]
      print(x)
      LCD.draw_rect(x, x, 0, 319, bytearray(l))
      print('done')

    # color = 0xFF00
    # last_pos = None
    # while True:
    #     get = LCD.touch_get()
    #     if get != None and get != last_pos:
    #         LCD.draw_point(get[0], get[1], mandelbrot(get[0]/480, get[1]/320))
            # color += 1
            # color &= 0xFFFF
#        time.sleep(0.001)





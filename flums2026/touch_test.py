from machine import Pin, SPI, PWM
import time
import struct
import framebuf

LCD_DC = 8
LCD_CS = 9
LCD_SCK = 10
LCD_MOSI = 11
LCD_MISO = 12
LCD_BL = 13
LCD_RST = 15
TP_CS = 16
TP_IRQ = 17

cs = Pin(LCD_CS, Pin.OUT)
rst = Pin(LCD_RST, Pin.OUT)
dc = Pin(LCD_DC, Pin.OUT)

tp_cs = Pin(TP_CS, Pin.OUT)
irq = Pin(TP_IRQ, Pin.IN)

def TouchGet():
  if irq() == 0:
    spi = SPI(1, 5_000_000, polarity=1, phase=1, sck=Pin(LCD_SCK),
                    mosi=Pin(LCD_MOSI), miso=Pin(LCD_MISO))
    tp_cs(0)
    X_Point = 0
    Y_Point = 0
    # print("irq=", irq(), end="\t")
    for i in range(0, 1):
        spi.write(bytearray([0XD0]))
        Read_data = spi.read(2)
        # print("y: ", Read_data,end="\t")
        Y_Point = Y_Point+(((Read_data[0] << 8)+Read_data[1]) >> 3)
        y_data = (Read_data[0] << 8) + Read_data[1]

        spi.write(bytearray([0X90]))
        Read_data = spi.read(2)
        # print("x: ", Read_data)
        X_Point = X_Point+(((Read_data[0] << 8)+Read_data[1]) >> 3)
        x_data = (Read_data[0] << 8) + Read_data[1]

    print("x_data: %04X\ty_data: %04X\tx_point: %04X\ty_point: %04X" %(x_data, y_data, X_Point, Y_Point), end="\n")
    X_Point = X_Point*1.0/3
    Y_Point = Y_Point*1.0/3
    # print("x_point: %s\ty_point: %s" % (X_Point, Y_Point))

    tp_cs(1)
    X_Point = min(480, max(0, int((X_Point-430)*480/3270)))
    Y_Point = min(320, max(0, 320-int((Y_Point-430)*320/3270)))
    Result_list = [X_Point, Y_Point]
    return(Result_list)


while True:
    t = TouchGet()
    if 0 and t:
        print("touch = ", t)
    time.sleep(0.01)
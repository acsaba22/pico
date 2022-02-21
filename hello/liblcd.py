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


def color_to_bytes(color):
    return struct.pack("H", color)

RED = 0x07E0
GREEN = 0x001f
BLUE = 0xf800
WHITE = 0xffff
BLACK = 0x0000


def RGB(r, g, b):
    color = 0
    color |= (r >> 3)
    color <<= 6;
    color |= (g >> 2)
    color <<= 5;
    color |= (b >> 3)
    return color

def RGB_FB(r, g, b):
    color = RGB(r, g, b)
    return (color>>8)+((color&0xFF) << 8)

  
class LCD_3inch5():

    def __init__(self):

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

        self.initDisplay()

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
        self.spi.write(bytearray([buf]))
        self.cs(1)

    def write_data_buffer(self, buf):
        for b in buf:
            self.write_data(b)
        return

    def initDisplay(self):
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

    def BackLight(self, duty):
        pwm = PWM(Pin(LCD_BL))
        pwm.freq(1000)
        if(duty >= 100):
            pwm.duty_u16(65535)
        else:
            pwm.duty_u16(655*duty)

    def ShowBuffer(self, x1, x2, y1, y2, buffer):
        self.write_cmd(0x2A)
        self.write_data_buffer([x1 >> 8, x1 & 0xFF, x2 >> 8, x2 & 0xFF])

        self.write_cmd(0x2B)
        self.write_data_buffer([y1 >> 8, y1 & 0xFF, y2 >> 8, y2 & 0xFF])

        self.write_cmd(0x2C)

        self.cs(1)
        self.dc(1)
        self.cs(0)
        self.spi.write(buffer)
        self.cs(1)

    def ShowBufferAtBox(self, box, buffer):
        self.ShowBuffer(box.x1, box.x2, box.y1, box.y2, buffer)

    def ShowPoint(self, x, y, color):
        self.ShowBuffer(int(x), int(x), int(y), int(y), bytearray(color_to_bytes(color)))
        
    def Clear(self, color = WHITE):
        b = bytearray(color_to_bytes(color) * 480 * 2 *4)
        for y in range(0, 320, 4):
            self.ShowBuffer(0, 479, y, y+3, b)
        

    def TouchGet(self):
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
            return(Result_list)


class SmartTouch(object):
    def __init__(self, screen):
        self.screen = screen
        self.reads = []
        self._last_pos = None
        self._read()
       
    # This needs to be called frequently, if .get() is not called often.
    def do(self):
        self._read()
        
    def get(self):
        self._read()
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


def clip_coord(coord, box):
    return Coord(
        min(box.x2, max(box.x1, coord.x)),
        min(box.y2, max(box.y1, coord.y)))


class Coord(object):
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def __eq__(self, other):
        return self.x == other.x and self.y == other.y

    def __repr__(self):
        return "(%d,%d)" % (self.x, self.y)

    def clip(self, box):
        self.x = min(box.x2, max(box.x1, self.x))
        self.y = min(box.y2, max(box.y1, self.y))

class Box(object):
    def __init__(self, x1, x2, y1, y2):
        self.x1 = x1
        self.x2 = x2
        self.y1 = y1
        self.y2 = y2

    def __repr__(self):
        return "(%d,%d,%d,%d)" % (self.x1, self.x2, self.y1, self.y2)

    def __contains__(self, point):
        clipped_point = clip_coord(point, self)
        return clipped_point == point

    def __add__(self, other):
        return Box(min(self.x1, other.x1), max(self.x2, other.x2),
                   min(self.y1, other.y1), max(self.y2, other.y2))

    def __mul__(self, other):
        return Box(max(self.x1, other.x1), min(self.x2, other.x2),
                   max(self.y1, other.y1), min(self.y2, other.y2))

    def is_valid(self):
        return (self.x1 <= self.x2) and (self.y1 <= self.y2)
    
    def min_size(self):
        return min(self.x2-self.x1, self.y2-self.y1)

    @property
    def width(self):
        return self.x2-self.x1+1

    @property
    def height(self):
        return self.y2-self.y1+1


DEFAULT_BG_COLOR = WHITE

def getImageBytesize(w, h):
    return w*h*2

class Sprite(object):
    def __init__(self, lcd, width, height, background_color=None):
        self.width = width
        self.height = height

        self.pos = Coord()
        expected_size = getImageBytesize(self.width, self.height)
        self.sprite = bytearray(expected_size)
        self.background = bytearray(color_to_bytes(background_color or DEFAULT_BG_COLOR) * width * height)
        self.lcd = lcd
        self.visible = False
        self._x_offset = - width//2
        self._y_offset = - height//2
        self._allowed_box = Box(-self._x_offset, 480 + self._x_offset, -self._y_offset, 320 + self._y_offset)

    def getBuffer(self):
        return self.sprite

    def setBuffer(self, buf):
        assert len(buf) == getImageBytesize(self.width, self.height)
        self.sprite = buf
    
    def getFramebuffer(self):
        return framebuf.FrameBuffer(self.sprite, self.width, self.height, framebuf.RGB565)

    def getBox(self):
        return Box(
            self.pos.x + self._x_offset,
            self.pos.x + self._x_offset + self.width-1,
            self.pos.y + self._y_offset,
            self.pos.y + self._y_offset + self.height-1)

    def undraw(self):
        if self.visible:
            self.lcd.ShowBufferAtBox(
                self.getBox(),
                self.background)

    def draw(self):
        if self.visible:
            self.lcd.ShowBufferAtBox(
                self.getBox(),
                self.sprite)

    def show(self):
        if not self.visible:
            self.visible = True
            self.draw()

    def hide(self):
        self.undraw()
        self.visible = False

    def move(self, target_pos, do_undraw=True):
        target_pos.clip(self._allowed_box)
        if self.pos == target_pos:
            self.draw()
            return
        if do_undraw:
            self.undraw()
        self.pos = target_pos
        self.draw()

    def moveBy(self, delta_x, delta_y, do_undraw=True):
        target = Coord(self.pos.x+delta_x, self.pos.y+delta_y)
        self.move(target, do_undraw)

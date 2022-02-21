import liblcd
import time
import framebuf
import math

class Button(object):
    COLOR = liblcd.RGB_FB(0, 127, 0)
    PRESSED_COLOR = liblcd.RGB_FB(0, 160, 0)
    TEXT_COLOR = liblcd.RGB_FB(0, 255, 0)
    LIGHT_COLOR = liblcd.RGB_FB(255, 0, 0)
    DARK_COLOR = liblcd.RGB_FB(0, 0, 255)
    
    def __init__(self, screen, box):
        self.screen = screen
        self.box = liblcd.Box(int(box.x1), int(box.x2), int(box.y1), int(box.y2))
        self.text = ""
        self._state = 0
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
    
    def _drawUpLeftEdge(self, fb, color):
        pass
    
    def _drawBottomRightEdge(self, fb, color):
        pass

    def _drawSurface(self, fb, color):
        fb.fill_rect(0, 0, self.box.width, self.box.height, color)

    def _drawNormal(self):        
        fb, buf = self._getFB()
        self._drawSurface(fb, self.COLOR)
        self._drawUpLeftEdge(fb, self.LIGHT_COLOR)
        self._drawBottomRightEdge(fb, self.DARK_COLOR)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4), self.box.height // 2 - 4, self.TEXT_COLOR)
        self.screen.ShowBufferAtBox(self.box, buf)

    def _drawPressed(self):
        fb, buf = self._getFB()
        self._drawSurface(fb, self.PRESSED_COLOR)
        self._drawUpLeftEdge(fb, self.DARK_COLOR)
        self._drawBottomRightEdge(fb, self.LIGHT_COLOR)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4)+2, self.box.height // 2 - 2, self.TEXT_COLOR)
        self.screen.ShowBufferAtBox(self.box, buf)
        
    def _setState(self, new_state):
        new_state = min(1, max(0, new_state))
        if self._state == new_state:
            return
        self._state = new_state
        self.draw()
        
    def do(self, touch):
        if touch:
            c = liblcd.Coord(touch[0], touch[1])
            if c in self.box:
                self._setState(1)
            else:
                self._setState(0)
        elif self._state == 1:
            self._setState(0)
            self.doPressed()
            return True
        return False
    
    def doPressed(self):
        print (self.text)
   
class Button3D(Button):
    def __init__(self, screen, box):
        Button.__init__(self, screen, box)
        
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

    def _drawSurface(self, fb, color):
        fb.fill_rect(2, 2, self.box.width - 4, self.box.height - 4, color)
   

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    screen.Clear()
    button = Button(screen, liblcd.Box(100, 200, 100, 150))
    button.setText("Press me 1")
    button2 = Button3D(screen, liblcd.Box(100, 200, 200, 250))
    button2.setText("Press me 2")
    while True:
        t = screen.TouchGet()
        button.do(t)
        button2.do(t)


if __name__ == '__main__':
    main()



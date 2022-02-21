import liblcd
import framebuf

class Button(object):
   
    def __init__(self, screen, box,
                 text="",
                 color_surface=liblcd.RGB_FB(128, 128, 128),
                 color_surface_pressed=liblcd.RGB_FB(160, 160, 160),
                 color_text=liblcd.RGB_FB(0, 0, 0)):
        self._state = 0

        self.screen = screen
        self.box = liblcd.Box(int(box.x1), int(box.x2), int(box.y1), int(box.y2))
        
        self.text = text
        self.color_surface = color_surface
        self.color_surface_pressed = color_surface_pressed
        self.color_text = color_text
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

    def _drawEdge(self, fb):
        pass

    def _drawSurface(self, fb):
        if self._state:
            fb.fill_rect(0, 0, self.box.width, self.box.height, self.color_surface)
        else:
            fb.fill_rect(0, 0, self.box.width, self.box.height, self.color_surface_pressed)            

    def _drawNormal(self):
        fb, buf = self._getFB()
        self._drawSurface(fb)
        self._drawEdge(fb)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4), self.box.height // 2 - 4, self.color_text)
        self.screen.ShowBufferAtBox(self.box, buf)

    def _drawPressed(self):
        fb, buf = self._getFB()
        self._drawSurface(fb)
        self._drawEdge(fb)
        if self.text:
            fb.text(self.text, max(0, self.box.width//2 - len(self.text)*4)+2, self.box.height // 2 - 2, self.color_text)
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
    def __init__(self, screen, box,
                 color_edge_dark=liblcd.RGB_FB(64, 64, 64),
                 color_edge_light=liblcd.RGB_FB(192, 192, 192),
                 **kwargs):
        self.color_edge_dark = color_edge_dark
        self.color_edge_light = color_edge_light
        Button.__init__(self, screen, box, kwargs)
        
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
        
    def _drawEdge(self, fb):
        if self._state:
            self._drawBottomRightEdge(fb, self.color_edge_light)
            self._drawUpLeftEdge(fb, self.color_edge_dark)
        else:
            self._drawBottomRightEdge(fb, self.color_edge_dark)
            self._drawUpLeftEdge(fb, self.color_edge_light)   

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



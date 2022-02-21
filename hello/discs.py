import liblcd
import time
import framebuf
import math

def init_board(lcd):
    b = bytearray([0xFF] * 480 * 2)
    for y in range(320):
        lcd.ShowBuffer(0, 479, y, y, b)

class Disc(object):
    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 40, 40)
        self.sprite.getFramebuffer().fill(liblcd.RED)
        self.reset()
    
    def reset(self):
        self.sprite.hide()
        self.face = 0

    def is_visible(self):
        return self.sprite.visible
    
    def move(self, target):
        self.sprite.move(target)
        
    def hide(self):
        self.sprite.hide()
        
    def show(self):
        self.sprite.show()

    def drawFace(self):
        if self.face == 0:
           self.sprite.getFramebuffer().fill(liblcd.RED)
        elif self.face == 1:
           self.sprite.getFramebuffer().fill(liblcd.GREEN)
        self.sprite.draw()
        
    def setFace(self, face):
        face = int(face)
        if self.face != face:
            self.face = min(1, max(0, face))
            self.drawFace()
    
    def toggleFace(self):
        self.setFace(1 - self.face)
            
    def getFace(self):
        return self.face
    
    def getBox(self):
        return self.sprite.getBox()

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    init_board(screen)
    pos = [liblcd.Coord(int(160+100*math.sin(2*3.1415*n/5)), int(160+100*math.cos(2*3.1415*n/5)))  for n in range(5)]
    discs = [Disc(screen) for _  in range(len(pos))]
    for i in range(len(pos)):
        disc = discs[i]
        disc.reset()
        disc.move(pos[i])
        disc.setFace(0)
        disc.show()

    last_touched = -1
    while True:
        touch = screen.TouchGet()
        if touch:
            c = liblcd.Coord(touch[0], touch[1])
            for i in range(len(pos)):
                disc = discs[i]
                if c in disc.getBox():
                    last_touched = i
        elif last_touched >= 0:
            discs[(last_touched+1)%len(discs)].toggleFace()
            discs[(last_touched-1)%len(discs)].toggleFace()
            last_touched = -1
        time.sleep(0.1)


if __name__ == '__main__':
    main()



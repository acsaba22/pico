import liblcd
import framebuf
import time

class Counter(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 96, 8)
        self.sprite.move(liblcd.Coord(10, 10))
        self.fb = self.sprite.getFramebuffer()
        self.reset()

    def reset(self):
        self.value = 0
        self.update()
        self.sprite.show()

    def update(self):
        self.fb.fill(liblcd.WHITE)
        self.fb.text("counter: %d" % (self.value, ), 0, 0, liblcd.BLACK)
        self.sprite.draw()

    def increase(self, by=1):
        self.value += by
        self.update()

    def hide(self):
        self.sprite.hide()


def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    screen.Clear()
    button = liblcd.Button(screen, liblcd.Box(100, 200, 100, 150))
    button.setText("UP")
    button2 = liblcd.Button3D(screen, liblcd.Box(100, 200, 200, 250))
    button2.setText("DOWN")
    button3 = liblcd.Button3D(screen, liblcd.Box(300, 479, 160, 319))
    counter = Counter(screen)
    touch = liblcd.SmartTouch(screen)
    while True:
        t = touch.get()
        if button.do(t):
            print ("up")
            counter.increase(1)
        if button2.do(t):
            print ("down")
            counter.increase(-1)
        if button3.do(t):
            return
        time.sleep(0.01)


if __name__ == '__main__':
    main()



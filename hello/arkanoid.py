import liblcd
import time
import framebuf


def init_board(lcd):
    b = bytearray([0xFF] * 480 * 2)
    for y in range(320):
        lcd.ShowBuffer(0, 479, y, y, b)


MIN_X, MAX_X = 5, 475
MIN_Y, MAX_Y = 5, 315


class Ball(object):
    BALL = bytearray(b'\xff\xff\xff\xff\xdeT\xc5-\xc4\xea\xcc\xaa\xc4\xcc\xcd\xf4\xff\xff\xff\xff\xff\xff\xc4*\xe5\x0c\xe4\xab\xec)\xf4\t\xdcK\xbcK\x9bj\xff\xff\xcd4\xa9\xa0\xfb%\xfaa\xfa!\xf9\xc1\xe9\x81\xcaEx\xe0\xbd4\xa9\x02\xd9\x00\xf9\xe0\xf9\xe0\xf9\xe0\xf9\x80\xf0\xc0\xd0\x80\x80\x00P\x82\x90\x00\xe8\xe0\xf9\x80\xf9\xc0\xf9\xa0\xf9@\xf0\xc0\xc8@\x88\x00(\x00p\x00\xd0\x80\xf9\x00\xf9 \xf9\x00\xf0\xc0\xe0\x80\xb8\x00x\x00(\x00p\xa2\xa8\x00\xd8\x80\xe8\xa0\xe8\xa0\xd8`\xc0\x00\x98\x00`\x00@\x82\xc5U`\x00\xa8\x00\xb8\x00\xc0\x00\xb0\x00\x90\x00h\x008\x00\xbdU\xff\xff\x82\xaaX\x00x\x00x\x00x\x00h\x00(\x00r\x8a\xff\xff\xff\xff\xff\xff\xbdUH\xa2(\x000\x00P\x82\xbdU\xff\xff\xff\xff')
    def __init__(self, lcd, player):
        self.player = player
        self.sprite = liblcd.Sprite(lcd, 10, 10, buffer=self.BALL)
        self.ball_dir = [6, 6]

    def reset(self):
        self.sprite.move(liblcd.Coord(240, 10))
        self.sprite.show()
        self.ball_dir = [6, 6]


    def is_visible(self):
        return self.sprite.visible

    def move(self):
        ball_pos = self.sprite.pos
        player_box = self.player.getBox()
        new_ball_pos = liblcd.Coord(
            ball_pos.x + self.ball_dir[0], ball_pos.y + self.ball_dir[1])
        if new_ball_pos.x < MIN_X or MAX_X < new_ball_pos.x:
            self.ball_dir[0] = -self.ball_dir[0]
        if MAX_Y < new_ball_pos.y:
            self.sprite.hide()
            return
        elif new_ball_pos.y < MIN_Y:
            self.ball_dir[1] = -self.ball_dir[1]
        elif player_box.x1 <= ball_pos.x < player_box.x2:
            if self.ball_dir[1] > 0:
                max_y = player_box.y1
            else:
                max_y = player_box.y2
            if ball_pos.y < max_y < new_ball_pos.y:
                self.ball_dir[1] = -self.ball_dir[1]
        self.sprite.moveBy(self.ball_dir[0], self.ball_dir[1])


class Player(object):
    PLAYER_WIDTH = 60
    MAX_SPEED = PLAYER_WIDTH // 4
    RACKET_60 = bytearray(b'\xff\xff\xff\xff\xff\xff[\rZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xecZ\xec[\rs\xd0\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff1\xc81\xa7)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f1\x869\xc7J\x8b\xff\xff\xff\xff\xff\xff)fBjBJ)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f)f!\x04!%)fB)\xff\xff)f1\xa7\x84sR\xed!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%!%\x18\xc3\x18\xc3!%)fJ\x8b!%!%9\xe8)\x87\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\xc3\x10\x82\x10\xa3)f)f1\xc7!F\x10\xa3\x10\xc3\x10\xa3\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x08b\x10\xa2\x18\xe4!\x04!%B)\x10\xa3\x10\x82\x10\x82\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x08a\x10\x82\x10\x82\x10\x82\x10\xa3\xff\xff)\x86\x10\xa2\x10\xa2\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x82\x10\x81\x10\x82\x08a\xff\xff\xff\xff\xff\xff9\xc8!\x04\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x18\xc3\x10\xa2\x18\xc3\xff\xff\xff\xff\xff\xff\xff\xff\xff\xff[\rJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJJB\x08B)\xff\xff\xff\xff\xff\xff')

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, self.PLAYER_WIDTH, 10, buffer=self.RACKET_60)
        self.target_pos = 240

    def reset(self):
        self.sprite.move(liblcd.Coord(240, 280))
        self.sprite.show()
        self.target_pos = 240

    def get_pos(self):
        return self.sprite.pos

    def getBox(self):
        return self.sprite.getBox()

    def hide(self):
        self.sprite.hide()

    def move(self):
        delta = 0
        if self.sprite.pos.x < self.target_pos:
            delta = min(self.MAX_SPEED, self.target_pos-self.sprite.pos.x)
        elif self.sprite.pos.x > self.target_pos:
            delta = -min(self.MAX_SPEED, self.sprite.pos.x-self.target_pos)
        self.sprite.moveBy(delta, 0)

class Score(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 96, 8)
        self.sprite.move(liblcd.Coord(10, 10))
        self.fb = self.sprite.getFramebuffer()
        self.score = 0

    def reset(self):
        self.score = 0
        self.update()
        self.sprite.show()

    def update(self):
        self.fb.fill(liblcd.WHITE)
        self.fb.text("score: %d" % (self.score, ), 0, 0, liblcd.BLACK)
        self.sprite.draw()

    def increase(self):
        self.score += 1
        self.update()

    def hide(self):
        self.sprite.hide()

class Text(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 160, 40)
        self.fb = self.sprite.getFramebuffer()
        self.fb.fill(liblcd.RED)
        self.sprite.move(liblcd.Coord(240, 150))

    def set_text(self, text_lines):
        assert len(text_lines) < self.sprite.height // 8
        top = self.sprite.height // 2 - len(text_lines)*4
        self.fb.fill(liblcd.RED)
        for line in text_lines:
            left = max(0, self.sprite.width // 2 - len(line)*4)
            self.fb.text(line, left, top, liblcd.BLACK)
            top += 8
        self.sprite.draw()

    def show(self):
        self.sprite.show()

    def hide(self):
        self.sprite.hide()

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    init_board(screen)
    player = Player(screen)
    ball = Ball(screen, player)
    text_box = Text(screen)
    score = Score(screen)
    while True:
        text_box.set_text(["Touch screen", "to start"]);
        text_box.show()
        while screen.TouchGet():
            pass
        while not screen.TouchGet():
            pass
        text_box.hide()
        player.reset()
        ball.reset()
        score.reset()
        last_time = time.time()
        while ball.is_visible():
            if last_time != time.time():
                last_time += 1
                score.increase()
            player.move()
            touch = screen.TouchGet()
            if touch:
                player.target_pos = touch[0]
            time.sleep(0.03)
            ball.move()
        player.hide()
        score.hide()
        text_box.set_text(["GAME OVER", "", "points: %d" % (score.score,)]);
        text_box.show()
        time.sleep(2)
        while not screen.TouchGet():
            pass
        text_box.hide()


if __name__ == '__main__':
    main()

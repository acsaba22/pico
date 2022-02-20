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
    def __init__(self, lcd, player):
        self.player = player
        self.sprite = liblcd.Sprite(lcd, 10, 10)
        self.sprite.get_framebuffer().fill(liblcd.RED)
        self.ball_dir = [6, 6]
    
    def reset(self):
        self.sprite.move(liblcd.Coord(240, 10))
        self.sprite.show()
        self.ball_dir = [6, 6]
        

    def is_visible(self):
        return self.sprite.visible
    
    def move(self):
        ball_pos = self.sprite.pos
        player_box = self.player.get_box()
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
        self.sprite.move_by(self.ball_dir[0], self.ball_dir[1])


class Player(object):
    PLAYER_WIDTH = 60
    MAX_SPEED = PLAYER_WIDTH // 4

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, self.PLAYER_WIDTH, 10)
        self.sprite.get_framebuffer().fill(liblcd.BLACK)
        self.target_pos = 240

    def reset(self):
        self.sprite.move(liblcd.Coord(240, 280))
        self.sprite.show()
        self.target_pos = 240

    def get_pos(self):
        return self.sprite.pos

    def get_box(self):
        return self.sprite.get_box()

    def hide(self):
        self.sprite.hide()
        
    def move(self):
        delta = 0
        if self.sprite.pos.x < self.target_pos:
            delta = min(self.MAX_SPEED, self.target_pos-self.sprite.pos.x)
        elif self.sprite.pos.x > self.target_pos:
            delta = -min(self.MAX_SPEED, self.sprite.pos.x-self.target_pos)
        self.sprite.move_by(delta, 0)

class Score(object):

    def __init__(self, lcd):
        self.sprite = liblcd.Sprite(lcd, 96, 8)
        self.sprite.move(liblcd.Coord(10, 10))
        self.fb = self.sprite.get_framebuffer()
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
        self.fb = self.sprite.get_framebuffer()
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

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
        self.ball_dir = [6, 6]
        self.ball_pos = (240, 160)
        self.buf = bytearray(10 * 10 * 2)
        self.background = bytearray([0xff] * 10 * 10 * 2)
        self.fb = framebuf.FrameBuffer(self.buf, 10, 10, framebuf.RGB565)
        self.lcd = lcd
        self.fb.fill(liblcd.RED)
        self.player = player

    def undraw_ball(self):
        self.lcd.ShowBuffer(
            self.ball_pos[0] - 5, self.ball_pos[0] + 4,
            self.ball_pos[1] - 5, self.ball_pos[1] + 4, self.background)

    def draw_ball(self):
        self.lcd.ShowBuffer(
            self.ball_pos[0] - 5, self.ball_pos[0] + 4,
            self.ball_pos[1] - 5, self.ball_pos[1] + 4, self.buf)

    def move_ball(self):
        self.undraw_ball()

        player_box = self.player.get_box()
        new_ball_pos = (
            self.ball_pos[0] + self.ball_dir[0], self.ball_pos[1] + self.ball_dir[1])
        if new_ball_pos[0] < MIN_X or MAX_X < new_ball_pos[0]:
            self.ball_dir[0] = -self.ball_dir[0]
        max_y = MAX_Y
        if player_box.x1 <= self.ball_pos[0] < player_box.x2:
            if self.ball_dir[1] > 0:
                max_y = self.player.get_box().y1
            else:
                max_y = self.player.get_box().y2
        if new_ball_pos[1] < MIN_Y or max_y < new_ball_pos[1]:
            self.ball_dir[1] = -self.ball_dir[1]
        self.ball_pos = (
            self.ball_pos[0] + self.ball_dir[0], self.ball_pos[1] + self.ball_dir[1])
        self.draw_ball()

class Player(object):
    PLAYER_WIDTH = 60
    MAX_SPEED = PLAYER_WIDTH // 4

    def __init__(self, lcd):
        buf = bytearray(self.PLAYER_WIDTH * 10 * 2)
        self.target_pos = 240
        fb = framebuf.FrameBuffer(
            buf, self.PLAYER_WIDTH, 10, framebuf.RGB565)
        fb.fill(liblcd.BLACK)
        self.sprite = liblcd.Sprite(lcd, buf, self.PLAYER_WIDTH, 10)
        self.sprite.move(liblcd.Coord(240, 280))
        self.sprite.show()

    def get_pos(self):
        return self.sprite.pos

    def get_box(self):
        return self.sprite.get_box()

    def move(self):
        delta = 0
        if self.sprite.pos.x < self.target_pos:
            delta = min(self.MAX_SPEED, self.target_pos-self.sprite.pos.x)
        elif self.sprite.pos.x > self.target_pos:
            delta = -min(self.MAX_SPEED, self.sprite.pos.x-self.target_pos)
        self.sprite.move_by(delta, 0)



def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    init_board(screen)
    player = Player(screen)
    ball = Ball(screen, player)
    while True:
        ball.move_ball()
        player.move()

        touch = screen.TouchGet()
        if touch:
            player.target_pos = touch[0]
        time.sleep(0.03)


if __name__ == '__main__':
    main()

import liblcd
import time
import framebuf


def init_board(lcd):
    b = bytearray([0xFF] * 480 * 2)
    for y in range(320):
        lcd.ShowBuffer(0, 479, y, y, b)


MIN_X, MAX_X = -235, 235
MIN_Y, MAX_Y = -155, 155


class Ball(object):
    def __init__(self, lcd, player):
        self.ball_dir = [6, 6]
        self.ball_pos = (0, 0)
        self.buf = bytearray(10 * 10 * 2)
        self.background = bytearray([0xff] * 10 * 10 * 2)
        self.fb = framebuf.FrameBuffer(self.buf, 10, 10, framebuf.RGB565)
        self.lcd = lcd
        self.fb.fill(lcd.RED)
        self.player = player

    def undraw_ball(self):
        self.lcd.ShowBuffer(
            self.ball_pos[0] + 235, self.ball_pos[0] + 244,
            self.ball_pos[1] + 155, self.ball_pos[1] + 164, self.background)

    def draw_ball(self):
        self.lcd.ShowBuffer(
            self.ball_pos[0] + 235, self.ball_pos[0] + 244,
            self.ball_pos[1] + 155, self.ball_pos[1] + 164, self.buf)

    def move_ball(self):
        self.undraw_ball()

        new_ball_pos = (
            self.ball_pos[0] + self.ball_dir[0], self.ball_pos[1] + self.ball_dir[1])
        if new_ball_pos[0] < MIN_X or MAX_X < new_ball_pos[0]:
            self.ball_dir[0] = -self.ball_dir[0]
        max_y = MAX_Y
        if self.player.pos - 30 < self.ball_pos[0] < self.player.pos + 30:
            max_y = self.player.PLAYER_Y - 152
        if new_ball_pos[1] < MIN_Y or max_y < new_ball_pos[1]:
            self.ball_dir[1] = -self.ball_dir[1]
        self.ball_pos = (
            self.ball_pos[0] + self.ball_dir[0], self.ball_pos[1] + self.ball_dir[1])
        self.draw_ball()


class Player(object):
    PLAYER_Y = 280
    PLAYER_WIDTH = 60
    MAX_SPEED = PLAYER_WIDTH // 4

    def __init__(self, lcd):
        self._low_x = 240 - self.PLAYER_WIDTH // 2
        self._high_x = self._low_x + self.PLAYER_WIDTH - 1

        self.target_pos = 0
        self.pos = 0
        self.buf = bytearray(self.PLAYER_WIDTH * 10 * 2)
        self.background = bytearray([0xff] * self.PLAYER_WIDTH * 10 * 2)
        self.fb = framebuf.FrameBuffer(
            self.buf, self.PLAYER_WIDTH, 10, framebuf.RGB565)
        self.lcd = lcd
        self.fb.fill(lcd.BLACK)
        self.draw()

    def undraw(self):
        self.lcd.ShowBuffer(
            self.pos + self._low_x, self.pos + self._high_x,
            self.PLAYER_Y, self.PLAYER_Y+9, self.background)

    def draw(self):
        self.lcd.ShowBuffer(
            self.pos + self._low_x, self.pos + self._high_x,
            self.PLAYER_Y, self.PLAYER_Y+9, self.fb)

    def move(self):
        self.target_pos = min(205, max(-205, self.target_pos))
        if self.pos == self.target_pos:
            self.draw()
            return
        self.undraw()
        if self.pos < self.target_pos:
            delta = min(self.MAX_SPEED, self.target_pos-self.pos)
        elif self.pos > self.target_pos:
            delta = -min(self.MAX_SPEED, self.pos-self.target_pos)
        self.pos += delta
        self.draw()


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
            player.target_pos = touch[0] - 240
        time.sleep(0.03)


if __name__ == '__main__':
    main()

import liblcd
import time

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    screen.Clear()
    bSki = liblcd.Button(screen, liblcd.Box(10, 110, 10, 50), "ski")
    bWolf = liblcd.Button(screen, liblcd.Box(10, 110, 60, 100), "wolf")
    bArkanoid = liblcd.Button(screen, liblcd.Box(10, 110, 110, 150), "arkanoid")
    bLab = liblcd.Button(screen, liblcd.Box(10, 110, 160, 200), "labyrinth")
    bGameOfLife = liblcd.Button(screen, liblcd.Box(10, 110, 210, 250), "GameOfLife")
    bPaint = liblcd.Button(screen, liblcd.Box(10, 110, 260, 300), "paint")
    bMandel1 = liblcd.Button(screen, liblcd.Box(130, 200, 260, 300), "mandel 1")
    bMandel2 = liblcd.Button(screen, liblcd.Box(130, 200, 210, 250), "mandel 2")
    bMandel3 = liblcd.Button(screen, liblcd.Box(130, 200, 160, 200), "mandel 3")
    bMandel4 = liblcd.Button(screen, liblcd.Box(130, 200, 110, 150), "mandel Z")
    bInstall = liblcd.Button(screen, liblcd.Box(250, 400, 10, 90), "install")
    bUninstall = liblcd.Button(screen, liblcd.Box(250, 400, 110, 120), "uninstall")
    bExit = liblcd.Button(screen, liblcd.Box(250, 400, 150, 270), "exit")
    touch = liblcd.SmartTouch(screen)
    while True:
        t = touch.get()
        if bSki.do(t):
            import ski as prog
            prog.main()
        if bPaint.do(t):
            import paint as prog
            prog.main()
        if bArkanoid.do(t):
            import arkanoid as prog
            prog.main()
        if bLab.do(t):
            import lab as prog
            prog.main()
        if bGameOfLife.do(t):
            import gameoflife as prog
            prog.main()
        if bWolf.do(t):
            import wolf as prog
            prog.main()
        if bMandel1.do(t):
            import mandelbrot as prog
            prog.main()
        if bMandel2.do(t):
            import mandelbrot_quick as prog
            prog.main()
        if bMandel3.do(t):
            import mandelbrot_window as prog
            prog.main()
        if bMandel4.do(t):
            import z_mandelbrot as prog
            prog.main()
        if bInstall.do(t):
            import os
            os.rename('start.py', 'main.py')
        if bUninstall.do(t):
            import os
            os.rename('main.py', 'start.py')
            return
        if bExit.do(t):
            return
        time.sleep(0.01)


if __name__ == '__main__':
    main()




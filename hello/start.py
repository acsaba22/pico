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
    bTorpedo  = liblcd.Button(screen, liblcd.Box(130, 200, 10, 50), "Torpedo")
    bSkiV2 = liblcd.Button(screen, liblcd.Box(130, 200, 110, 150), "ski v2")
    bMandelZ = liblcd.Button(screen, liblcd.Box(130, 200, 160, 200), "mandel Z")
    bMandel2 = liblcd.Button(screen, liblcd.Box(130, 200, 210, 250), "mandel 2")
    bMandel1 = liblcd.Button(screen, liblcd.Box(130, 200, 260, 300), "mandel 1")
    bDisc = liblcd.Button(screen, liblcd.Box(130, 200, 60, 100), "Disc")
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
        if bMandelZ.do(t):
            import z_mandelbrot as prog
            prog.main()
        if bDisc.do(t):
            import discs as prog
            prog.main()
        if bTorpedo.do(t):
            from mains import torpedo as prog
            prog.main()
        if bSkiV2.do(t):
            from mains import skiV2 as prog
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




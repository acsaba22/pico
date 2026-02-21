from timestats import NewTimer
import timestats
import jobs

MAX_ITERATION = 255
ABS_LIMIT = 100
N = 30

MandelTimer = NewTimer('Mandel')

def mandelbrot(x, y):
    with MandelTimer:
        c = complex(x, y)
        z = complex(0, 0)
        step = 0
        while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
            step += 1
            z = z*z + c
        return step

async def mandelTest():
    xmin = -2
    xmax = 1
    ymin = -1
    ymax = 1
    x = xmin
    sum = 0
    for ix in range(N):
        if ix % 10 == 0:
            print(N-ix)
        y = ymin
        for iy in range(N):
            y += (ymax-ymin) / N
            sum += mandelbrot(x, y)
        x += (xmax-xmin) / N
    print(f"Total mandel steps: {sum} avg: {sum//(N*N)}")
    timestats.stats.report()
    jobs.STOP.set()

async def main():
    # jobs.start(timestats.stats.run())
    jobs.start(mandelTest())
    await jobs.STOP.wait()

if __name__ == '__main__':
    jobs.runMain(main())

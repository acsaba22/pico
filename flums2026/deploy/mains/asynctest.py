import asyncio
import timestats
import sys
import jobs
from timestats import Timer


MAX_ITERATION = 100
ABS_LIMIT = 100

mandelTimer = Timer("Main.Mandelbrot")
mandelSingleTimer = Timer("mandelbrotSingle", mandelTimer)
mandel1 = Timer("mandelStep1")
mandel2 = Timer("mandelStep2")

def mandelbrot(x, y):
    with mandelSingleTimer:
        c = complex(x, y)
        z = complex(0, 0)
        step = 0
        while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
            step += 1
            z = z*z+c
        return step


async def main1():
    while True:
        z = 0
        n = 0
        with mandelTimer:
            for x in range(-10, 11, 1):
                for y in range(-10, 11, 1):
                    z += mandelbrot(x/10, y/10)
                    n += 1
        print(f"N = {n}, total iter: {z}, avg iter: {z / n:.1f}")
        await asyncio.sleep_ms(0)

async def main():
    jobs.start(main1())
    jobs.start(timestats.stats.run())
    await jobs.STOP.wait()

jobs.runMain(main())

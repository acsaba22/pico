# import mandelbrot

MAX_ITERATION = 100
ABS_LIMIT = 100


def mandelbrot(x, y):
    c = complex(x, y)
    z = complex(0, 0)
    step = 0
    while step < MAX_ITERATION and abs(z) < ABS_LIMIT:
        step += 1
        z = z**2 + c
    return step


print(mandelbrot(0.9, 0.2))

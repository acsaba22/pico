import liblcd
import time
import framebuf
import math


def draw_line1(screen, x1,y1,x2,y2,c):
    if int(x1) == int(x2):
        for y in range(min(y1, y2),max(y1, y2)+1):
            screen.ShowPoint(int(x1), int(y), c)
    elif int(y1) == int(y2):
        for x in range(min(x1, x2),max(x1, x2)+1):
            screen.ShowPoint(int(x), int(y1), c)
    elif max(abs(y1/y2), abs(y2/y1)) > max(abs(x1/x2), abs(x2/x1)):
        if y1 > y2:
            t = x1
            x1, x2 = x2, t
            t = y1
            y1, y2 = y2, t
        x = x1
        dx = (x2-x1)/(y2-y1)
        for y in range(y1, y2+1):
            screen.ShowPoint(int(x), int(y), c)
            x += dx
        screen.ShowPoint(int(x2), int(y), c)
    else:
        if x1 > x2:
            t = x1
            x1, x2 = x2, t
            t = y1
            y1, y2 = y2, t
        y = y1
        dy = (y2-y1)/(x2-x1)
        for x in range(x1, x2+1):
            screen.ShowPoint(int(x), int(y), c)
            y += dy
        screen.ShowPoint(int(x), int(y2), c)

def draw_line15(screen, x1,y1,x2,y2,c):
    x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
    if x1 == x2 or y1 == y2:
        screen.FillBuffer(min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2), c)
    elif max(abs(y1/y2), abs(y2/y1)) > max(abs(x1/x2), abs(x2/x1)):
        if y1 > y2:
            t = x1
            x1, x2 = x2, t
            t = y1
            y1, y2 = y2, t
        x = x1
        dx = (x2-x1)/(y2-y1)
        for y in range(y1, y2+1):
            screen.ShowPoint(int(x), int(y), c)
            x += dx
        screen.ShowPoint(int(x2), int(y), c)
    else:
        if x1 > x2:
            t = x1
            x1, x2 = x2, t
            t = y1
            y1, y2 = y2, t
        y = y1
        dy = (y2-y1)/(x2-x1)
        for x in range(x1, x2+1):
            screen.ShowPoint(int(x), int(y), c)
            y += dy
        screen.ShowPoint(int(x), int(y2), c)

def draw_line2(screen, x1,y1,x2,y2,c):
    x1, x2, y1, y2 = int(x1), int(x2), int(y1), int(y2)
    if x1 == x2 or y1 == y2:
        screen.FillBuffer(min(x1, x2), max(x1, x2), min(y1, y2), max(y1, y2), c)
    elif max(abs(y1/y2), abs(y2/y1)) > max(abs(x1/x2), abs(x2/x1)):
        if y1 > y2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        x = x1
        dx = (x2-x1)/(y2-y1)
        last_draw = None
        for y in range(y1, y2+1):
            if not last_draw:
                last_draw = (int(x), y)
            elif last_draw[0] == int(x):
                pass
            else:
                screen.FillBuffer(last_draw[0], last_draw[0], last_draw[1], y-1, c)
                last_draw = (int(x), y)
            x += dx
        if last_draw:
            screen.FillBuffer(last_draw[0], last_draw[0], last_draw[1], y2, c)
    else:
        if x1 > x2:
            x1, x2 = x2, x1
            y1, y2 = y2, y1
        y = y1
        dy = (y2-y1)/(x2-x1)
        last_draw = None
        for x in range(x1, x2+1):
            if not last_draw:
                last_draw = (x, int(y))
            elif last_draw[1] == int(y):
                pass
            else:
                screen.FillBuffer(last_draw[0], x-1, last_draw[1], last_draw[1], c)
                last_draw = (x, int(y))
            y += dy
        if last_draw:
            screen.FillBuffer(last_draw[0], x2, last_draw[1], last_draw[1], c)

draw_line = draw_line2

def clock(screen):
    r = 100
#    while True:
    if 1:
        for d in range(0, 360, 6):
            x, y = math.sin(d/180*3.141592), math.cos(d/180*3.141592)
            draw_line(screen, 240,160,240+r*x,160+r*y, liblcd.BLACK)
            draw_line(screen, 240,160,240+r*x,160+r*y, liblcd.WHITE)
            
CAM = [3, 3, -10]
ZOOM = 150

def draw_360(screen, orig_points, edges):
    global CAM, ZOOM
    N = len(orig_points)
    for d in range(0, 360, 6):
        CAM[0], CAM[1] = math.sin(d/180*3.141592)*5, math.cos(d/180*3.141592)*5
        
        points = [((p[0]+CAM[0])/(CAM[2]+p[2]), (p[1]+CAM[1])/(CAM[2]+p[2])) for p in orig_points]
        points = [(ZOOM*p[0]+240, ZOOM*p[1]+160) for p in points]
        for e in edges:
            p1, p2, c = points[e[0]], points[e[1]], e[2]
            draw_line(screen, p1[0], p1[1], p2[0], p2[1], c)
#        time.sleep(0.1)
        for e in edges:
            p1, p2 = points[e[0]], points[e[1]]
            draw_line(screen, p1[0], p1[1], p2[0], p2[1], liblcd.WHITE)

def cube(screen):
    b = liblcd.BLACK
    orig_points = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),
                   (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1)]
    edges = [(0,1,b), (1,2,b), (2,3,b), (3,0,b), (4,5,b), (5,6,b), (6,7,b), (7,4,b),
             (0,4,b), (1,5,b), (2,6,b), (3,7,b)]
    draw_360(screen, orig_points, edges)

    orig_points = [(-1, -1, -1), ( 1, -1, -1), ( 1,  1, -1), (-1,  1, -1),
                   (-1, -1,  1), ( 1, -1,  1), ( 1,  1,  1), (-1,  1,  1),
                   (1, 3, -1), (-1, 3, -1),
                   ]
    
    g = liblcd.RGB_FB(0, 255, 0)
    w = liblcd.WHITE
    edges = [(1,2,b), (2,3,b), (3,0,b), (5,6,b), (6,7,b), (7,4,b),
             (2,6,b), (3,7,b), (2,8,b), (8,9,b), (9,3,b)]
    draw_360(screen, orig_points, edges)

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(100)
    screen.Clear()
    ts = time.ticks_ms()
#    clock(screen)
    cube(screen)
    te = time.ticks_ms()
    print (time.ticks_diff(te, ts))

if __name__ == '__main__':
    main()


import liblcd

def main():
    screen = liblcd.LCD_3inch5()
    screen.BackLight(70)
    touch = liblcd.SmartTouch(screen)

    color = 0xFF00
    while True:      
        t = touch.get()
        if t:
            screen.ShowPoint(t[0], t[1], color)
            color += 1
            color &= 0xFFFF



if __name__=='__main__':
    main()



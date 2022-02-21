
import pygame

image = pygame.image.load("data/disc-red.png")
out = open("data/disc-red.txt", "w")
buffer = bytearray((image.get_height()) * image.get_width() * 2)
i = 0

for y in range(image.get_height()):
    for x in range(image.get_width()):
        color = 0
        pixel = image.get_at((x, y))
        color |= (pixel.r >> 3)
        color <<= 6;
        color |= (pixel.g >> 2)
        color <<= 5;
        color |= (pixel.b >> 3)
        buffer[i] = color >> 8
        buffer[i+1] = color & 0xFF
        i += 2
#    print (buffer[:i])
#    break
out.write("width = %d\n" % (image.get_width(), ))
out.write("height = %d\n" % (image.get_height(), ))
out.write("buf = %s\n" % (repr(buffer), ))
print(len(buffer))
#print(repr(buffer))
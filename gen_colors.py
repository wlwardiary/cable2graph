from colorsys import hsv_to_rgb
from random import randint, uniform

places = open('data/embassy.list').readlines()

for place in places:
    h = uniform(0.1, 1)
    s = uniform(0.3, 0.8)
    v = uniform(0.30, 0.95)
    r, g, b = hsv_to_rgb(h, s, v)
    r, g, b = [x*255 for x in (r, g, b)]

    print "#vertices .%s circle { fill: rgba(%i,%i,%i,0.8); }" % (place.strip(), r, g, b)

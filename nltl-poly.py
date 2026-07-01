import datetime
import random
import sys

from PIL import Image, ImageDraw


def draw_nltl_shape_one(image, starting_point, size, fill_colour):
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [
            starting_point,
            ((size / 4) * 3, (size / 4)),
            ((size / 4) * 3, size),
            (0, size),
        ],
        fill=fill_colour,
    )


def draw_nltl_shape_two(image, starting_point, size, fill_colour):
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [
            starting_point,
            ((size / 4) * 3, (size / 4)),
            ((size / 4) * 3, size),
            (size, size),
        ],
        fill=fill_colour,
    )


def draw_nltl_shape_three(image, starting_point, size, fill_colour):
    draw = ImageDraw.Draw(image)
    draw.polygon(
        [starting_point, ((size / 4) * 3, (size / 4)), (size, 0)], fill=fill_colour
    )


canvas = 4800
white = (255, 255, 255)

for i in range(100):
    # pink = (223 + random.randint(-10, 10),164 + random.randint(-10, 10),227 + random.randint(-10, 10))
    # im = Image.new("RGB", (canvas, canvas), white)
    # draw_nltl_shape_one(im1, (0,0), canvas, pink)
    # im.save("looped-output/shape-" + i + ".jpg", "JPEG")
    print(i)

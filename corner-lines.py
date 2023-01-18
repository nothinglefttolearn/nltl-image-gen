import sys
from PIL import Image, ImageDraw
canvas = 4800

# corner shape 1
im1 = Image.new("RGB", (canvas, canvas), (0,153,153))
draw = ImageDraw.Draw(im1)
draw.line([
    (0, 0), 
    ((canvas/4)*3, (canvas/4)),
    ((canvas/4)*3, canvas)
], fill=(153,0,153), width=3)
im1.save("corner-shape-1.jpg", "JPEG")


# corner shape 1
im2 = Image.new("RGB", (canvas, canvas), (0,153,153),)
draw = ImageDraw.Draw(im2)
draw.line([
    (canvas, 0), 
    ((canvas/4)*3, (canvas/4)),
    ((canvas/4)*3, canvas)
], fill=(153,0,153), width=3)
im2.save("corner-shape-2.jpg", "JPEG")

# corner shape 1
im3 = Image.new("RGB", (canvas, canvas), (0,153,153))
draw = ImageDraw.Draw(im3)
draw.line([
    (0, 0), 
    ((canvas/4)*3, (canvas/4)),
    (canvas, 0)
], fill=(153,0,153), width=3)
im3.save("corner-shape-3.jpg", "JPEG")
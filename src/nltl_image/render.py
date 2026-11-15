"""Turn shapes into images.

Rendering happens in two steps, and each one is a building block in its own right:

1. ``shape_mask`` rasterises a shape into a greyscale ("L") mask: 255 inside
   the shape, 0 outside. It says *where* the shape is.
2. ``fill`` paints a colour through a mask onto a background. It says *what*
   the shape looks like.

Effects that change the outline (distortion, roughening, blur) can work on
the mask, and effects that change the surface (texture, grain) can work on
the filled image, without either needing to know about shape geometry.
"""

import nltl_values
from PIL import Image, ImageColor, ImageDraw

from nltl_image.geometry import shape_points

TRANSPARENT = (0, 0, 0, 0)


def shape_mask(shape_name: str, size: int, padding: int = 0) -> Image.Image:
    """A ``size`` x ``size`` "L" mask of the named shape."""
    mask = Image.new("L", (size, size), 0)
    ImageDraw.Draw(mask).polygon(shape_points(shape_name, size, padding), fill=255)
    return mask


def fill(mask: Image.Image, color: str, background: str | None = None) -> Image.Image:
    """Paint ``color`` through ``mask`` onto a background, returning an RGBA image.

    Colours are anything Pillow's ``ImageColor`` understands, e.g. ``"#DFA4E3"``.
    The background is transparent when ``background`` is None.
    """
    bg = ImageColor.getrgb(background) if background else TRANSPARENT
    image = Image.new("RGBA", mask.size, bg)
    image.paste(ImageColor.getrgb(color), mask=mask)
    return image


def render(
    shape_name: str,
    color_name: str,
    size: int,
    padding: int = 0,
    background: str | None = None,
) -> Image.Image:
    """A ``size`` x ``size`` RGBA image of a named shape in a named nltl colour.

    Raises ``ValueError`` for out-of-range padding or an unparseable background,
    and ``KeyError`` for an unknown shape or colour name.
    """
    mask = shape_mask(shape_name, size, padding)
    return fill(mask, nltl_values.color(color_name), background)

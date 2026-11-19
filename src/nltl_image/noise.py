"""Seeded, resolution-independent noise fields as greyscale ("L") images.

Noise is the raw material for organic effects. Everything here is driven by a
``random.Random`` so a given seed always produces the same image, and feature
sizes are fractions of the image edge so the result looks the same at any
resolution.
"""

import math
import random

from PIL import Image, ImageOps


def value_noise(
    size: int, cells: float, rng: random.Random, stretch: float = 1.0
) -> Image.Image:
    """Smooth random blobs roughly ``size / cells`` px across.

    A small grid of random values is upscaled bicubically. ``stretch`` > 1
    elongates the blobs horizontally by that factor.
    """
    w = max(2, math.ceil(cells / stretch)) + 1
    h = max(2, math.ceil(cells)) + 1
    grid = Image.frombytes("L", (w, h), rng.randbytes(w * h))
    return grid.resize((size, size), Image.Resampling.BICUBIC)


def fractal_noise(
    size: int,
    scale: float,
    rng: random.Random,
    octaves: int = 4,
    persistence: float = 0.5,
    stretch: float = 1.0,
    angle: float = 0.0,
) -> Image.Image:
    """Multi-octave noise with a uniform histogram over 0..255.

    ``scale`` is the largest feature size as a fraction of ``size``. Each
    octave halves the feature size and weights it by ``persistence``. Blobs
    are elongated by ``stretch`` along ``angle`` (degrees, counter-clockwise
    from the x axis).

    The result is histogram-equalised, so thresholding at ``255 * (1 - p)``
    selects very nearly a fraction ``p`` of the pixels.
    """
    if octaves < 1:
        raise ValueError(f"octaves must be at least 1, got {octaves}")
    # Draw oversized so rotation never exposes empty corners.
    big = math.ceil(size * math.sqrt(2)) if angle % 180 else size
    cells = (big / size) / scale
    field = value_noise(big, cells, rng, stretch)
    weight_total = 1.0
    weight = persistence
    for octave in range(1, octaves):
        layer = value_noise(big, cells * 2**octave, rng, stretch)
        weight_total += weight
        field = Image.blend(field, layer, weight / weight_total)
        weight *= persistence

    if angle % 180:
        field = field.rotate(angle, Image.Resampling.BICUBIC)
        offset = (big - size) // 2
        field = field.crop((offset, offset, offset + size, offset + size))
    return ImageOps.equalize(field)


def linear_ramp(size: int, angle: float = 0.0) -> Image.Image:
    """A 0..255 gradient rising along ``angle`` (degrees, counter-clockwise
    from the x axis), spanning the full image in that direction."""
    big = math.ceil(size * math.sqrt(2))
    # linear_gradient runs top (0) to bottom (255); turn it to run along +x.
    ramp = Image.linear_gradient("L").rotate(90).resize((big, big))
    ramp = ramp.rotate(angle, Image.Resampling.BILINEAR)
    offset = (big - size) // 2
    ramp = ramp.crop((offset, offset, offset + size, offset + size))
    return ImageOps.autocontrast(ramp)

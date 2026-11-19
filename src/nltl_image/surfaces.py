"""Surfaces: effects that make the whole image look like it is on a material.

A surface takes a filled RGBA image and returns a new one with the same size
and exactly the same alpha channel: it changes colour only, never where ink
is or how transparent anything is. Each surface is a frozen dataclass of its
settings; randomness comes in through ``apply``::

    image = fill(shape_mask("face", 2160), "#DFA4E3", background="#FFFFFF")
    Canvas(depth=0.4).apply(image, random.Random(7)).save("face.png")
"""

import math
import random
from dataclasses import dataclass
from functools import cache
from typing import Any, ClassVar, Protocol

from PIL import Image, ImageChops, ImageOps, ImageStat

from nltl_image.noise import fractal_noise

# Pixels per thread while drawing the weave. Below this a thread's rounded
# profile turns into a stair-step, so small images are drawn larger and then
# scaled down.
_MIN_THREAD_PX = 8


class Surface(Protocol):
    name: ClassVar[str]
    # Effects are dataclasses; this lets type checkers accept them in
    # dataclasses.asdict() and fields().
    __dataclass_fields__: ClassVar[dict[str, Any]]

    def apply(self, image: Image.Image, rng: random.Random) -> Image.Image: ...


def _check_fraction(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


@dataclass(frozen=True, kw_only=True)
class Canvas:
    """Artist's cotton canvas: a plain over-under weave of uneven threads.

    Colour is lightened on the raised threads and darkened in the gaps
    between them, on the ink and the background alike.

    ``weave``        thread spacing as a fraction of the image edge
                     (0.006 is about 170 threads across).
    ``depth``        how strongly the weave shades colour (0..1).
    ``irregularity`` how much threads vary in thickness and stray from
                     straight (0 = a perfect machine grid).
    ``mottle``       strength of broad, uneven patches in the ground (0..1).
    """

    name: ClassVar[str] = "canvas"

    weave: float = 0.006
    depth: float = 0.3
    irregularity: float = 0.5
    mottle: float = 0.3

    def __post_init__(self) -> None:
        if not 0 < self.weave <= 0.5:
            raise ValueError(f"weave must be in (0, 0.5], got {self.weave}")
        _check_fraction("depth", self.depth)
        _check_fraction("irregularity", self.irregularity)
        _check_fraction("mottle", self.mottle)

    def apply(self, image: Image.Image, rng: random.Random) -> Image.Image:
        if not self.depth:
            return image.copy()
        size = image.width
        flat = Image.new("L", image.size, 128)
        shade = Image.blend(flat, self.relief(size, rng), self.depth)
        # Hard light leaves colour alone where shade is 128, lightens above
        # it and darkens below it, so the weave shows on white and on black.
        rgb = ImageChops.hard_light(
            image.convert("RGB"), Image.merge("RGB", (shade,) * 3)
        )
        result = rgb.convert("RGBA")
        result.putalpha(image.getchannel("A"))
        return result

    def relief(self, size: int, rng: random.Random) -> Image.Image:
        """The canvas height map as an "L" image: averages 128, raised
        threads above it, gaps below it."""
        threads = max(2, round(1 / self.weave))
        cell = max(_MIN_THREAD_PX, math.ceil(size / threads))
        edge = threads * cell

        warp_tile, weft_tile = _weave_tiles(cell)
        warp, weft = _tile(warp_tile, edge), _tile(weft_tile, edge)
        if self.irregularity:
            warp = ImageChops.multiply(warp, self._thickness(threads, edge, rng))
            weft = ImageChops.multiply(
                weft,
                self._thickness(threads, edge, rng).transpose(
                    Image.Transpose.TRANSPOSE
                ),
            )
        relief = ImageChops.lighter(warp, weft)
        if self.irregularity:
            relief = self._wobble(relief, threads, cell, rng)
        if edge != size:
            relief = relief.resize((size, size), Image.Resampling.BICUBIC)
        if self.mottle:
            patches = fractal_noise(size, 0.3, rng, octaves=3)
            relief = Image.blend(relief, patches, self.mottle * 0.5)
        return _centre(ImageOps.autocontrast(relief, cutoff=0.5))

    def _thickness(self, threads: int, edge: int, rng: random.Random) -> Image.Image:
        """Per-thread thickness for vertical threads, as a 0..255 multiplier
        that drifts slowly along each thread's length."""
        lengthwise = max(2, threads // 3)
        drop = self.irregularity * 0.8
        values = bytes(
            round(255 * (1 - drop * rng.random())) for _ in range(threads * lengthwise)
        )
        grid = Image.frombytes("L", (threads, lengthwise), values)
        # Smooth along the thread, then widen each column to a full thread.
        grid = grid.resize((threads, edge), Image.Resampling.BICUBIC)
        return grid.resize((edge, edge), Image.Resampling.NEAREST)

    def _wobble(
        self, image: Image.Image, threads: int, cell: int, rng: random.Random
    ) -> Image.Image:
        """Bend the threads gently by warping the image through a jittered grid."""
        edge = image.width
        steps = max(2, threads // 8)
        amount = self.irregularity * 0.7 * cell

        def jitter(i: int) -> float:
            # Keep the border still so nothing is pulled in from outside.
            return 0.0 if i in (0, steps) else rng.uniform(-amount, amount)

        grid = [
            [
                (gx * edge / steps + jitter(gx), gy * edge / steps + jitter(gy))
                for gx in range(steps + 1)
            ]
            for gy in range(steps + 1)
        ]
        mesh = []
        for gy in range(steps):
            for gx in range(steps):
                box = (
                    round(gx * edge / steps),
                    round(gy * edge / steps),
                    round((gx + 1) * edge / steps),
                    round((gy + 1) * edge / steps),
                )
                corners = (
                    grid[gy][gx],
                    grid[gy + 1][gx],
                    grid[gy + 1][gx + 1],
                    grid[gy][gx + 1],
                )
                mesh.append((box, [c for point in corners for c in point]))
        return image.transform(
            image.size, Image.Transform.MESH, mesh, Image.Resampling.BILINEAR
        )


@cache
def _weave_tiles(cell: int) -> tuple[Image.Image, Image.Image]:
    """Height of the vertical (warp) and horizontal (weft) threads over one
    2 x 2 repeat of a plain weave, ``cell`` px per thread.

    Each thread is a rounded ridge. Where it passes over the crossing thread
    it bulges up in the middle of the cell; where it passes under, only its
    flanks show, low down.
    """

    def across(t: float) -> float:
        # Threads fill ~85% of their cell; the rest is gap.
        return max(0.0, math.cos(math.pi * (t - 0.5) / 0.85))

    def over(t: float) -> float:
        return 0.55 + 0.45 * math.sin(math.pi * t)

    under = 0.25
    side = 2 * cell
    warp, weft = bytearray(side * side), bytearray(side * side)
    for y in range(side):
        v = (y % cell + 0.5) / cell
        for x in range(side):
            u = (x % cell + 0.5) / cell
            warp_on_top = (x // cell + y // cell) % 2 == 0
            warp[y * side + x] = round(
                255 * across(u) * (over(v) if warp_on_top else under)
            )
            weft[y * side + x] = round(
                255 * across(v) * (under if warp_on_top else over(u))
            )
    return (
        Image.frombytes("L", (side, side), bytes(warp)),
        Image.frombytes("L", (side, side), bytes(weft)),
    )


def _tile(tile: Image.Image, edge: int) -> Image.Image:
    """Repeat ``tile`` to fill an ``edge`` x ``edge`` image."""
    row = Image.new("L", (edge, tile.height))
    for x in range(0, edge, tile.width):
        row.paste(tile, (x, 0))
    out = Image.new("L", (edge, edge))
    for y in range(0, edge, tile.height):
        out.paste(row, (0, y))
    return out


def _centre(image: Image.Image) -> Image.Image:
    """Shift brightness so the image averages 128."""
    offset = round(128 - ImageStat.Stat(image).mean[0])
    return image.point(lambda v: min(255, max(0, v + offset)))


SURFACES: dict[str, type[Surface]] = {cls.name: cls for cls in (Canvas,)}

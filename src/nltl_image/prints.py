"""Prints: effects that decide where ink lands.

A print turns a shape mask into a new "L" mask that is never larger than the
original, so the result drops straight into ``fill``. Each print is a frozen
dataclass of its settings; randomness comes in through ``apply``::

    mask = Screenprint(ink=0.6).apply(shape_mask("face", 2160), random.Random(7))
    fill(mask, "#DFA4E3").save("face.png")
"""

import random
from dataclasses import dataclass
from typing import Any, ClassVar, Protocol

from PIL import Image, ImageChops, ImageFilter, ImageOps

from nltl_image.noise import fractal_noise, linear_ramp


class Print(Protocol):
    name: ClassVar[str]
    # Effects are dataclasses; this lets type checkers accept them in
    # dataclasses.asdict() and fields().
    __dataclass_fields__: ClassVar[dict[str, Any]]

    def apply(self, mask: Image.Image, rng: random.Random) -> Image.Image: ...


def _threshold(image: Image.Image, level: int) -> Image.Image:
    return image.point(lambda v: 255 if v >= level else 0)


def _check_fraction(name: str, value: float) -> None:
    if not 0 <= value <= 1:
        raise ValueError(f"{name} must be in [0, 1], got {value}")


@dataclass(frozen=True, kw_only=True)
class Screenprint:
    """An ink-starved screen print: the shape is there, the fill is patchy.

    The gaps are shaped like liquid. A noise field picks where ink made it
    through the mesh, then a few rounds of blur-and-rethreshold (a cheap
    mean-curvature flow) do what surface tension does to wet ink: edges
    round off, thin bridges pinch into droplets and tiny specks vanish.

    ``ink``     roughly the fraction of the shape that gets ink (0..1).
    ``pull``    direction the squeegee travels, in degrees counter-clockwise
                from rightward (270 = top to bottom). Blobs streak along it.
    ``starve``  how much faster the ink runs out towards the end of the
                pull (0 = evenly patchy, 1 = almost all at the start).
    ``scale``   size of the largest patches, as a fraction of the image.
    ``tension`` surface-tension strength, as a fraction of the image: higher
                gives rounder, smoother, fewer gaps.
    """

    name: ClassVar[str] = "screenprint"

    ink: float = 0.7
    pull: float = 270.0
    starve: float = 0.5
    scale: float = 0.12
    tension: float = 0.002

    def __post_init__(self) -> None:
        _check_fraction("ink", self.ink)
        _check_fraction("starve", self.starve)

    def apply(self, mask: Image.Image, rng: random.Random) -> Image.Image:
        size = mask.width

        # Streaky, multi-scale field: big mottling down to fine pinholes. A
        # high persistence keeps enough fine detail that transition zones
        # break up into droplets and pinholes rather than a few smooth lobes.
        field = fractal_noise(
            size,
            self.scale,
            rng,
            octaves=7,
            persistence=0.8,
            stretch=1.5,
            angle=self.pull,
        )
        if self.starve:
            # Ink is plentiful where the pull starts and runs dry where it ends.
            supply = ImageOps.invert(linear_ramp(size, self.pull))
            field = ImageOps.equalize(Image.blend(field, supply, self.starve))

        coverage = _threshold(field, round(255 * (1 - self.ink)))

        # Surface tension: repeated smoothing of the wet boundary.
        radius = max(1.0, self.tension * size)
        for _ in range(3):
            coverage = _threshold(
                coverage.filter(ImageFilter.GaussianBlur(radius)), 128
            )

        # Anti-alias the ink edges, then clip to the stencil.
        coverage = coverage.filter(ImageFilter.GaussianBlur(max(0.6, size / 3000)))
        return ImageChops.multiply(coverage, mask)


PRINTS: dict[str, type[Print]] = {cls.name: cls for cls in (Screenprint,)}

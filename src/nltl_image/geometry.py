"""Map nltl-values shapes from unit-square coordinates to pixel coordinates."""

from collections.abc import Iterable

import nltl_values

type Point = tuple[float, float]


def to_pixels(points: Iterable[Point], size: int, padding: int = 0) -> list[Point]:
    """Scale unit-square ``points`` onto a ``size`` px square inset by ``padding``.

    The unit square maps to the inner square ``[padding, size - padding)``, so
    shapes drawn with the same size and padding line up exactly.
    """
    if not 0 <= padding < size / 2:
        raise ValueError(f"padding must be in [0, {size / 2:g}), got {padding}")

    # Pillow fills polygons inclusive of their edge pixels, so the last pixel
    # of the inner square is at size - padding - 1, not size - padding.
    scale = size - 2 * padding - 1
    return [(padding + x * scale, padding + y * scale) for x, y in points]


def shape_points(shape_name: str, size: int, padding: int = 0) -> list[Point]:
    """Pixel coordinates of the named nltl-values shape."""
    return to_pixels(nltl_values.shape(shape_name).points, size, padding)

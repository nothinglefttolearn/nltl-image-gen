"""Generate images of the nltl shapes.

The public API is re-exported here, so callers import from ``nltl_image``
rather than its submodules::

    from nltl_image import render

    render("face", "primary", 2400, padding=200).save("face.png")
"""

from nltl_image.geometry import shape_points, to_pixels
from nltl_image.render import fill, render, shape_mask

__all__ = ["fill", "render", "shape_mask", "shape_points", "to_pixels"]

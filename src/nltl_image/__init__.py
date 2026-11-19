"""Generate images of the nltl shapes.

The public API is re-exported here, so callers import from ``nltl_image``
rather than its submodules::

    from nltl_image import Canvas, Recipe, Screenprint, render, save

    recipe = Recipe("face", "primary", 2160, surfaces=[Canvas()])
    save(render(recipe), recipe, "face.png")
"""

from nltl_image.geometry import shape_points, to_pixels
from nltl_image.noise import fractal_noise
from nltl_image.presets import builtin_presets, load_preset, preset_recipe
from nltl_image.prints import PRINTS, Print, Screenprint
from nltl_image.recipe import Recipe, read_recipe, save
from nltl_image.render import fill, render, shape_mask
from nltl_image.surfaces import SURFACES, Canvas, Surface

__all__ = [
    "PRINTS",
    "SURFACES",
    "Canvas",
    "Print",
    "Recipe",
    "Screenprint",
    "Surface",
    "builtin_presets",
    "fill",
    "fractal_noise",
    "load_preset",
    "preset_recipe",
    "read_recipe",
    "render",
    "save",
    "shape_mask",
    "shape_points",
    "to_pixels",
]

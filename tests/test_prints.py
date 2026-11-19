import random
from dataclasses import FrozenInstanceError

import pytest
from PIL import Image, ImageChops

from nltl_image import PRINTS, Screenprint, shape_mask

SIZE = 400
# A full square, so coverage of the image is coverage of the shape.
SQUARE = Image.new("L", (SIZE, SIZE), 255)


def coverage(mask, box=None):
    """Fraction of ``mask`` (or of ``box`` within it) that is inked."""
    region = mask.crop(box) if box else mask
    return sum(i * n for i, n in enumerate(region.histogram())) / (
        255 * region.width * region.height
    )


def printed(mask=SQUARE, seed=0, **settings):
    return Screenprint(**settings).apply(mask, random.Random(seed))


def test_never_inks_outside_the_shape():
    face = shape_mask("face", SIZE)
    outside = ImageChops.subtract(printed(face), face)
    assert outside.getbbox() is None


def test_full_ink_without_starving_prints_the_whole_shape():
    assert coverage(printed(ink=1, starve=0)) > 0.99


def test_ink_is_roughly_the_fraction_covered():
    amounts = [coverage(printed(ink=i)) for i in (0.3, 0.6, 0.9)]
    assert amounts == pytest.approx([0.3, 0.6, 0.9], abs=0.08)


def test_ink_runs_out_along_the_pull():
    result = printed(ink=0.6, starve=0.8, pull=270)
    top = coverage(result, (0, 0, SIZE, SIZE // 3))
    bottom = coverage(result, (0, 2 * SIZE // 3, SIZE, SIZE))
    assert top > bottom + 0.3


def test_same_rng_seed_makes_prints_repeatable():
    assert ImageChops.difference(printed(seed=5), printed(seed=5)).getbbox() is None


@pytest.mark.parametrize("settings", [{"ink": 1.5}, {"starve": -0.1}])
def test_rejects_out_of_range_settings(settings):
    with pytest.raises(ValueError):
        Screenprint(**settings)


def test_settings_are_frozen():
    with pytest.raises(FrozenInstanceError):
        Screenprint().ink = 0.1


def test_registered_by_name():
    assert PRINTS["screenprint"] is Screenprint
    assert Screenprint.name == "screenprint"

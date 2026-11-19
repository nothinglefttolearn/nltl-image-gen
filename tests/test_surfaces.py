import random

import pytest
from PIL import Image, ImageChops, ImageStat

from nltl_image import SURFACES, Canvas, Screenprint, fill, shape_mask

SIZE = 600
RNG = random.Random


def flat(color="#808080", size=SIZE):
    return Image.new("RGBA", (size, size), color)


def spread(image):
    """Standard deviation of brightness: 0 for a perfectly flat image."""
    return ImageStat.Stat(image.convert("L")).stddev[0]


def same(a, b):
    return ImageChops.difference(a, b).getbbox() is None


def test_never_changes_transparency():
    mask = Screenprint(ink=0.5).apply(shape_mask("face", SIZE), RNG(0))
    image = fill(mask, "#DFA4E3")
    assert same(Canvas().apply(image, RNG(0)).getchannel("A"), image.getchannel("A"))


def test_shades_ink_and_background():
    image = fill(shape_mask("face", SIZE), "#DFA4E3", background="#FFFFFF")
    out = Canvas().apply(image, RNG(0))
    ink, background = (0, SIZE // 2, SIZE // 4, SIZE), (SIZE // 2, 0, SIZE, SIZE // 4)
    assert spread(out.crop(ink)) > 2
    assert spread(out.crop(background)) > 2


def test_keeps_the_colour_on_average():
    out = Canvas().apply(flat(), RNG(0))
    assert ImageStat.Stat(out.convert("L")).mean[0] == pytest.approx(128, abs=8)


def test_more_depth_is_stronger():
    shallow, deep = (Canvas(depth=d).apply(flat(), RNG(0)) for d in (0.1, 0.6))
    assert spread(deep) > 2 * spread(shallow)


def test_zero_depth_changes_nothing():
    image = flat("#123456")
    assert same(Canvas(depth=0).apply(image, RNG(0)), image)


def test_weave_repeats_every_two_threads():
    # 20 threads across 600 px: 30 px per thread, and a plain weave repeats
    # over two threads. Without irregularity or mottle it is exactly periodic.
    out = Canvas(weave=0.05, irregularity=0, mottle=0, depth=1).apply(flat(), RNG(0))
    out = out.convert("L")

    def shifted_difference(dx):
        a = out.crop((0, 0, SIZE - 60, SIZE))
        b = out.crop((dx, 0, SIZE - 60 + dx, SIZE))
        return ImageStat.Stat(ImageChops.difference(a, b)).mean[0]

    assert shifted_difference(60) < 1
    assert shifted_difference(30) > 5


def test_same_rng_seed_is_repeatable():
    a, b = (Canvas().apply(flat(), RNG(3)) for _ in range(2))
    assert same(a, b)


@pytest.mark.parametrize(
    "settings",
    [{"depth": 1.5}, {"depth": -0.1}, {"weave": 0}, {"weave": 0.6}, {"mottle": 2}],
)
def test_rejects_out_of_range_settings(settings):
    with pytest.raises(ValueError):
        Canvas(**settings)


def test_registered_by_name():
    assert SURFACES["canvas"] is Canvas

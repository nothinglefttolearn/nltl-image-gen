import nltl_values
import pytest
from PIL import ImageChops

from nltl_image import Recipe, fill, palette, render, shape_mask

SIZE = 1000


@pytest.mark.parametrize("padding", [0, 1, 100, 333])
def test_padding_is_equal_on_every_side(padding):
    # space touches all four sides of the unit square, so its bounding box is
    # exactly the inner square.
    inner = (padding, padding, SIZE - padding, SIZE - padding)
    assert shape_mask("space", SIZE, padding).getbbox() == inner


@pytest.mark.parametrize("variant", ["", "2", "3"])
@pytest.mark.parametrize("padding", [0, 100])
def test_face_and_space_tile_the_inner_square(padding, variant):
    inner = (padding, padding, SIZE - padding, SIZE - padding)
    union = ImageChops.lighter(
        shape_mask(f"face{variant}", SIZE, padding),
        shape_mask(f"space{variant}", SIZE, padding),
    )
    assert union.crop(inner).getextrema() == (255, 255), "gap between face and space"
    assert union.getbbox() == inner


def test_fill_paints_colour_only_inside_mask():
    image = fill(shape_mask("face", SIZE), "#123456", background="#FFFFFF")
    assert image.getpixel((0, SIZE - 1)) == (0x12, 0x34, 0x56, 255)
    assert image.getpixel((SIZE - 1, 0)) == (255, 255, 255, 255)


def test_background_defaults_to_transparent():
    assert render(Recipe("face", "primary", SIZE)).getpixel((SIZE - 1, 0)) == (
        0,
        0,
        0,
        0,
    )


def test_render_uses_named_nltl_colour():
    pixel = render(Recipe("face", "secondary", SIZE)).getpixel((0, SIZE - 1))
    assert pixel == (0x87, 0x9B, 0x87, 255)


@pytest.mark.parametrize("shape", nltl_values.shape_names())
def test_every_nltl_values_shape_renders(shape):
    assert render(Recipe(shape, "primary", 64)).getbbox() is not None


def test_render_accepts_a_palette_background():
    image = render(Recipe("face", "primary", SIZE, background="canvas"))
    expected = fill(shape_mask("face", SIZE), "#000000", palette.color("canvas"))
    assert image.getpixel((SIZE - 1, 0)) == expected.getpixel((SIZE - 1, 0))


def test_render_rejects_a_web_colour():
    with pytest.raises(KeyError, match="unknown colour"):
        render(Recipe("face", "accent", 64))

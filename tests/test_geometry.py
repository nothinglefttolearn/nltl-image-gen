import pytest

from nltl_image import to_pixels

UNIT_SQUARE = [(0, 0), (1, 0), (1, 1), (0, 1)]


def test_unit_square_fills_canvas_without_padding():
    assert to_pixels(UNIT_SQUARE, 100) == [(0, 0), (99, 0), (99, 99), (0, 99)]


def test_padding_insets_every_side_equally():
    assert to_pixels(UNIT_SQUARE, 100, padding=10) == [
        (10, 10),
        (89, 10),
        (89, 89),
        (10, 89),
    ]


@pytest.mark.parametrize("padding", [-1, 50])
def test_rejects_out_of_range_padding(padding):
    with pytest.raises(ValueError, match="padding"):
        to_pixels(UNIT_SQUARE, 100, padding)

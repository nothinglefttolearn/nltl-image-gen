import nltl_values
import pytest

from nltl_image import palette


def test_names_are_the_art_palette_without_its_group():
    names = palette.color_names()
    assert {"primary", "secondary", "canvas"} <= set(names)
    assert names == sorted(
        path.removeprefix("art.")
        for path in nltl_values.colors()
        if path.startswith("art.")
    )


def test_web_colours_are_not_in_the_palette():
    assert "accent" not in palette.color_names()
    with pytest.raises(KeyError, match="unknown colour 'web.accent'"):
        palette.color("web.accent")


def test_color_looks_up_the_art_group():
    assert palette.color("primary") == nltl_values.color("art.primary")


def test_every_palette_colour_is_opaque_hex():
    for name in palette.color_names():
        assert len(palette.color(name)) == 7, name


@pytest.mark.parametrize(
    ("value", "expected"),
    [
        ("canvas", nltl_values.color("art.canvas")),
        ("#FFFFFF", "#FFFFFF"),
        ("red", "red"),
    ],
)
def test_resolve_names_palette_colours_and_passes_others_through(value, expected):
    assert palette.resolve(value) == expected

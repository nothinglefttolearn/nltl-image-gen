"""The nltl colours: nltl-values' art palette, by short name.

nltl-values groups its colours (``brand.*``, ``web.*``, ``art.*``). Only the
art palette is used here, and recipes, presets and the CLI name its colours
without the group (``"primary"``, not ``"art.primary"``) so recipes saved
before the grouping still render. See docs/adr/0001.

    palette.color("primary")           # "#DFA4E3"
    palette.resolve("canvas")          # "#F3EEE3"
    palette.resolve("#FFFFFF")         # "#FFFFFF", not a palette name
"""

import nltl_values

GROUP = "art"
_PREFIX = f"{GROUP}."


def color_names() -> list[str]:
    """Short names of every palette colour, sorted."""
    return sorted(
        path.removeprefix(_PREFIX)
        for path in nltl_values.colors()
        if path.startswith(_PREFIX)
    )


def color(name: str) -> str:
    """Hex value of the palette colour ``name``. Raises ``KeyError`` if unknown."""
    try:
        return nltl_values.colors()[_PREFIX + name]
    except KeyError:
        raise KeyError(
            f"unknown colour {name!r}; choose from {', '.join(color_names())}"
        ) from None


def resolve(value: str) -> str:
    """A palette colour's hex if ``value`` names one, otherwise ``value`` as
    given (a hex or other colour Pillow understands)."""
    return color(value) if value in color_names() else value

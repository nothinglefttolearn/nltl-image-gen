"""Command-line front end: arguments -> Recipe -> render -> save.

Settings layer as recipe defaults < --preset < explicit options. --print and
--surface choose effects; their options (--ink, --depth, ...) only adjust an
effect that is active. No rendering logic lives here.
"""

import argparse
import os
from datetime import datetime
from pathlib import Path
from typing import Any

import nltl_values

from nltl_image import palette
from nltl_image.presets import RECIPE_KEYS, builtin_presets, load_preset, preset_recipe
from nltl_image.prints import PRINTS
from nltl_image.recipe import DEFAULT_SIZE, save
from nltl_image.render import render
from nltl_image.surfaces import SURFACES

OUTPUT_DIR = Path("output")
OUTPUT_DIR_ENV = "NLTL_IMAGE_OUTPUT_DIR"
NONE = "none"

# Effect options: which kind of effect and which effect each one adjusts.
EFFECT_OPTIONS = {
    "ink": ("print", "screenprint"),
    "pull": ("print", "screenprint"),
    "weave": ("surface", "canvas"),
    "depth": ("surface", "canvas"),
}

EXAMPLES = """\
examples:
  nltl-image                                          # flat face, primary, 2160px
  nltl-image --shape space --color secondary
  nltl-image --shape face3 --background canvas        # palette background
  nltl-image --print screenprint --ink 0.6 --seed 7
  nltl-image --surface canvas --background '#FFFFFF'
  nltl-image --preset canvas-print --ink 0.7          # preset, one setting changed
  nltl-image --preset my-look.toml --surface none     # your preset, minus canvas

Every image carries its recipe (all settings and the seed) as metadata.
"""


def build_parser() -> argparse.ArgumentParser:
    presets = "\n".join(
        f"  {name:<14} {description}" for name, description in builtin_presets().items()
    )
    parser = argparse.ArgumentParser(
        prog="nltl-image",
        description="Render an nltl shape in an nltl colour onto a square image.",
        epilog=f"{EXAMPLES}\nbuilt-in presets:\n{presets}",
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--preset", metavar="NAME|FILE", help="built-in preset name or .toml path"
    )
    parser.add_argument("--shape", choices=nltl_values.shape_names())
    parser.add_argument("--color", choices=palette.color_names())
    parser.add_argument(
        "--size", type=int, help=f"image edge in pixels (default {DEFAULT_SIZE})"
    )
    parser.add_argument(
        "--padding",
        type=int,
        help="empty margin in pixels on every side (default 0: shape fills the square)",
    )
    parser.add_argument(
        "--background",
        help="colour of the material: a palette colour or e.g. '#FFFFFF' "
        "(default: transparent)",
    )

    prints = parser.add_argument_group("print: where ink lands")
    prints.add_argument("--print", choices=[*sorted(PRINTS), NONE])
    prints.add_argument(
        "--ink",
        type=float,
        help="screenprint: fraction of the shape that gets ink, 0-1 (default 0.7)",
    )
    prints.add_argument(
        "--pull",
        type=float,
        help="screenprint: squeegee direction in degrees counter-clockwise from "
        "rightward; ink runs out towards the end (default 270, top to bottom)",
    )

    surfaces = parser.add_argument_group("surface: the material it is printed on")
    surfaces.add_argument("--surface", choices=[*sorted(SURFACES), NONE])
    surfaces.add_argument(
        "--weave",
        type=float,
        help="canvas: thread spacing as a fraction of the image edge "
        "(default 0.006, about 170 threads across)",
    )
    surfaces.add_argument(
        "--depth",
        type=float,
        help="canvas: how strongly the weave shades colour, 0-1 (default 0.3)",
    )

    parser.add_argument(
        "--seed", type=int, help="fixes every random choice (default: random)"
    )
    parser.add_argument(
        "--output",
        type=Path,
        help=f"output path, .png or .jpg (default: named PNG in ${OUTPUT_DIR_ENV}, "
        f"or {OUTPUT_DIR}/ if unset)",
    )
    return parser


def layer(preset: dict[str, Any], args: argparse.Namespace) -> dict[str, Any]:
    """Explicit command-line choices layered over a loaded preset."""
    layered = {k: v for k, v in preset.items() if k in RECIPE_KEYS}
    layered |= {k: v for k in RECIPE_KEYS if (v := getattr(args, k)) is not None}

    for kind in ("print", "surface"):
        table = {name: dict(s) for name, s in preset.get(kind, {}).items()}
        match getattr(args, kind):
            case None:
                pass
            case "none":
                table = {}
            case chosen if chosen not in table:
                table = {chosen: {}}
        layered[kind] = table

    for option, (kind, effect) in EFFECT_OPTIONS.items():
        if (value := getattr(args, option)) is None:
            continue
        if effect not in layered[kind]:
            raise ValueError(f"--{option} needs --{kind} {effect}")
        layered[kind][effect][option] = value
    return layered


def output_dir() -> Path:
    """Where auto-named images go: $NLTL_IMAGE_OUTPUT_DIR, else ./output."""
    if value := os.environ.get(OUTPUT_DIR_ENV):
        return Path(value).expanduser()
    return OUTPUT_DIR


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        preset = load_preset(args.preset) if args.preset else {}
        recipe = preset_recipe(layer(preset, args), seed=args.seed)
        path: Path = args.output or output_dir() / "-".join(
            [
                "nltl",
                recipe.shape,
                recipe.color,
                *([Path(args.preset).stem] if args.preset else []),
                f"{datetime.now():%Y%m%d-%H%M%S}",
                f"s{recipe.seed}.png",
            ]
        )
        image = render(recipe)
        path.parent.mkdir(parents=True, exist_ok=True)
        save(image, recipe, path)
    except ValueError as e:
        parser.error(str(e))
    print(f"saved {path} (seed {recipe.seed})")

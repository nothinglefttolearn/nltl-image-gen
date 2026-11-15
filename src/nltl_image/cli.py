"""Render one nltl shape in one nltl colour onto a square image.

Shapes and colours come from nltl-values, the shared source of truth:

    nltl-image                                   # face, primary
    nltl-image --shape space --color secondary
    nltl-image --padding 400                     # 400px margin on every side

Shape coordinates are defined on the unit square; the unit square is mapped
onto the image minus --padding on each side, so face and space images rendered
with the same size and padding line up exactly. The background is transparent
unless --background is given. Output goes to output/ (created if missing).
"""

import argparse
from datetime import datetime
from pathlib import Path

import nltl_values

from nltl_image.render import render

OUTPUT_DIR = Path("output")
DEFAULT_SIZE = 4800
JPEG_SUFFIXES = {".jpg", ".jpeg"}


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="nltl-image",
        description=__doc__,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("--shape", choices=nltl_values.shape_names(), default="face")
    parser.add_argument(
        "--color", choices=sorted(nltl_values.colors()), default="primary"
    )
    parser.add_argument(
        "--size", type=int, default=DEFAULT_SIZE, help="image edge in pixels"
    )
    parser.add_argument(
        "--padding",
        type=int,
        default=0,
        help="empty margin in pixels on every side (default 0: shape fills the square)",
    )
    parser.add_argument(
        "--background",
        help="background colour, e.g. '#FFFFFF' (default: transparent)",
    )
    parser.add_argument(
        "--output",
        type=Path,
        help="output path (default: timestamped PNG in output/)",
    )
    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)

    path: Path = args.output or OUTPUT_DIR / (
        f"nltl-{args.shape}-{args.color}-{datetime.now():%Y%m%d-%H%M%S}.png"
    )
    is_jpeg = path.suffix.lower() in JPEG_SUFFIXES
    if is_jpeg and not args.background:
        parser.error("JPEG has no transparency; pass --background")

    try:
        image = render(args.shape, args.color, args.size, args.padding, args.background)
    except ValueError as e:
        parser.error(str(e))

    path.parent.mkdir(parents=True, exist_ok=True)
    if is_jpeg:
        image.convert("RGB").save(path, quality=95)
    else:
        image.save(path)
    print(f"saved {path}")

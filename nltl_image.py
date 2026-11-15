"""Render one nltl shape in one nltl colour onto a square image.

Shapes and colours come from nltl-values, the shared source of truth:

    uv run nltl_image.py                              # face, primary
    uv run nltl_image.py --shape space --color secondary
    uv run nltl_image.py --padding 400                # 400px margin on every side

Shape coordinates are defined on the unit square; the unit square is mapped
onto the image minus --padding on each side, so face and space images rendered
with the same size and padding line up exactly. The background is transparent
unless --background is given. Output goes to output/ (created if missing).
"""

import argparse
from datetime import datetime
from pathlib import Path

import nltl_values
from PIL import Image, ImageColor, ImageDraw

OUTPUT_DIR = Path("output")
DEFAULT_SIZE = 4800
JPEG_SUFFIXES = {".jpg", ".jpeg"}


def render(
    shape_name: str,
    color_name: str,
    size: int,
    padding: int = 0,
    background: str | None = None,
) -> Image.Image:
    """Return a ``size`` x ``size`` RGBA image of the named shape in the named colour.

    Raises ``ValueError`` for out-of-range padding or an unparseable background,
    and ``KeyError`` for an unknown shape or colour name.
    """
    if not 0 <= padding < size / 2:
        raise ValueError(f"padding must be in [0, {size / 2:g}), got {padding}")

    shape = nltl_values.shape(shape_name)
    fill = ImageColor.getrgb(nltl_values.color(color_name))
    bg = ImageColor.getrgb(background) if background else (0, 0, 0, 0)

    # Pillow fills polygons inclusive of their edge pixels, so the last pixel
    # of the inner square is at padding + inner - 1, not padding + inner.
    scale = size - 2 * padding - 1
    points = [(padding + x * scale, padding + y * scale) for x, y in shape.points]

    image = Image.new("RGBA", (size, size), bg)
    ImageDraw.Draw(image).polygon(points, fill=fill)
    return image


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter
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


if __name__ == "__main__":
    main()

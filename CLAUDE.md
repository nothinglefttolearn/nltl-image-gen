# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

`nltl_image` is a packaged Python project (src layout) that renders nltl
shapes into images with Pillow. It is expected to grow into many styles,
effects and processing steps built on a shared set of building blocks.

Shape geometry and colour values are **not** defined here — they come from
the `nltl-values` package (git dependency pinned to a tag in
`pyproject.toml` under `[tool.uv.sources]`). Never hard-code points or hex
values; to change them, release a new nltl-values tag and bump the pin.

## Tooling

- `mise.toml` pins Python and uv; `python.uv_venv_auto` activates `.venv`.
- uv manages dependencies (`pyproject.toml` + `uv.lock`) and builds with
  `uv_build`. The distribution is `nltl-image-gen` but the import name is
  `nltl_image` (`[tool.uv.build-backend] module-name`). `uv sync` installs it
  editable, so source changes apply without reinstalling.
- CLI: `uv run nltl-image ...` (`[project.scripts]` → `nltl_image.cli:main`)
  or `python -m nltl_image`.
- Dev tools are in the `dev` dependency group and wrapped as mise tasks:
  `mise run test | lint | format`, and `mise run check` (format check + lint +
  test, read-only) before committing.

## Layout

```
src/nltl_image/
  __init__.py   public API, re-exported from the modules below
  geometry.py   unit-square shape points -> pixel points (padding lives here)
  render.py     shape_mask (where), fill (what colour), render (both)
  cli.py        argparse front end; no rendering logic of its own
  __main__.py   python -m nltl_image
tests/          one test module per source module
```

Dependencies point one way: `cli` → `render` → `geometry` → `nltl_values`.
Keep the CLI thin; anything reusable belongs in the library modules.

## Rendering model

- nltl-values shapes are in unit-square coordinates, screen orientation
  (y down). The unit square maps onto the image inset by `padding` px on
  every side, so `face` and `space` at the same size/padding tile exactly.
- Pillow fills polygons inclusive of edge pixels, so points are scaled by
  `size - 2 * padding - 1` to keep padding symmetric.
- The core building block is the greyscale "L" mask from `shape_mask`.
  Outline effects (distortion, roughening) should transform masks; surface
  effects (texture, grain) should transform filled images. New styles compose
  these rather than re-drawing polygons.
- Default CLI output is a transparent PNG in `output/` (gitignored); JPEG
  output requires `--background`.

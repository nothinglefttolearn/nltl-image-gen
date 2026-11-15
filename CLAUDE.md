# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

A single script, `nltl_image.py`, that renders one nltl shape in one nltl
colour onto a square image with Pillow. Tests live in `tests/` (pytest);
ruff handles formatting and linting.

Shape geometry and colour values are **not** defined here — they come from
the `nltl-values` package (git dependency pinned to a tag in
`pyproject.toml` under `[tool.uv.sources]`). Never hard-code points or hex
values; to change them, release a new nltl-values tag and bump the pin.

## Tooling

- `mise.toml` pins Python and uv; `python.uv_venv_auto` activates `.venv`.
- uv manages dependencies (`pyproject.toml` + `uv.lock`). It is a non-packaged
  project (`tool.uv.package = false`); run with `uv run nltl_image.py ...`.
- Dev tools are in the `dev` dependency group (installed by `uv sync`) and
  wrapped as mise tasks in `mise.toml`: `mise run test | lint | format`, and
  `mise run check` (format check + lint + test, read-only) before committing.

## Rendering model

- nltl-values shapes are in unit-square coordinates, screen orientation
  (y down). The unit square maps onto the image inset by `--padding` px on
  every side, so `face` and `space` at the same size/padding tile exactly.
- Pillow fills polygons inclusive of edge pixels, so points are scaled by
  `inner - 1` to keep padding symmetric.
- Default output is a transparent PNG in `output/` (gitignored); JPEG output
  requires `--background`.

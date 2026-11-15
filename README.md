# nltl-image-gen

Generate square images of the nltl shapes (`face`, `space`) in the nltl
colours (`primary`, `secondary`). Shapes and colours come from
[nltl-values](https://github.com/nothinglefttolearn/nltl-values), pinned in
`pyproject.toml`.

```bash
mise install    # python + uv, pinned in mise.toml
uv sync         # pillow + nltl-values, pinned in uv.lock

uv run nltl-image                                      # face, primary, 4800px
uv run nltl-image --shape space --color secondary
uv run nltl-image --padding 400                     # 400px margin on all sides
uv run nltl-image --background '#FFFFFF' --size 2400
```

Images are transparent PNGs written to `output/` as
`nltl-<shape>-<color>-<timestamp>.png`; pass `--output` to choose a path.
`python -m nltl_image` works too, and inside the mise-activated venv plain
`nltl-image` does.

The same building blocks are importable:

```python
from nltl_image import fill, render, shape_mask

render("face", "primary", 2400, padding=200).save("face.png")
fill(shape_mask("space", 2400), "#000000", background="#FFFFFF")
```

## Development

```bash
mise run test        # pytest (extra args pass through: mise run test -k padding)
mise run lint        # ruff check
mise run format      # ruff format
mise run check       # format check + lint + test, changes nothing
```

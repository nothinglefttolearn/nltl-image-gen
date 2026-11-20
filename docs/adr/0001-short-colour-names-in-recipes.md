# Short colour names in recipes

nltl-values v0.5.0 split its colours into `brand.*`, `web.*` and `art.*`, so
`primary` became `art.primary`. We only ever use the `art` palette, so recipes,
presets, filenames and `--color` keep the short name (`"primary"`) and the
`art.` prefix is added in one place, `palette.py`, when looking it up. Every
saved image embeds its recipe; storing full paths would have left every image
made before the split with a recipe that no longer renders, or needed a
migration, for a prefix that never varies.

## Consequences

- A recipe's colour is not a valid nltl-values path on its own; anything
  reading recipes outside this project must add `art.`.
- If this project ever needs colours from another group, short names become
  ambiguous and this decision needs revisiting.

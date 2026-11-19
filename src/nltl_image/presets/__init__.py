"""Presets: named, partial recipes for reuse.

A preset is a TOML file. It can set any recipe field except the seed, name
effects and their settings in ``[print.<name>]`` and ``[surface.<name>]``
tables, and ``extends`` another preset (a built-in name or a file path,
relative to the extending file)::

    description = "A good pull on canvas, a little heavier"
    extends = "canvas-print"

    [surface.canvas]
    depth = 0.45

Built-ins live next to this module as ``<name>.toml``. Loading resolves
``extends`` by deep-merging the preset over its base, so settings in the
extending file win.
"""

import tomllib
from importlib.resources import files
from pathlib import Path
from typing import Any

from nltl_image.prints import PRINTS
from nltl_image.recipe import Recipe, build_effect
from nltl_image.surfaces import SURFACES

RECIPE_KEYS = {"shape", "color", "size", "padding", "background"}
PRESET_KEYS = RECIPE_KEYS | {"description", "extends", "print", "surface"}

_BUILTINS = files(__name__)


def builtin_presets() -> dict[str, str]:
    """Built-in preset names mapped to their one-line descriptions."""
    return {
        path.name.removesuffix(".toml"): tomllib.loads(path.read_text()).get(
            "description", ""
        )
        for path in sorted(_BUILTINS.iterdir(), key=lambda p: p.name)
        if path.name.endswith(".toml")
    }


def load_preset(name_or_path: str) -> dict[str, Any]:
    """Load a preset by built-in name or file path, with ``extends`` resolved.

    Raises ``ValueError`` for an unknown name, a bad key, a seed, or a
    preset that (indirectly) extends itself.
    """
    return _load(name_or_path, base_dir=Path.cwd(), seen=())


def preset_recipe(preset: dict[str, Any], seed: int | None = None) -> Recipe:
    """Turn a loaded preset into a ``Recipe``. Fields the preset leaves out
    keep the recipe defaults; with no ``seed`` a random one is chosen."""
    fields = {k: v for k, v in preset.items() if k in RECIPE_KEYS}
    fields["prints"] = [
        build_effect("print", PRINTS, {"name": name, **settings})
        for name, settings in preset.get("print", {}).items()
    ]
    fields["surfaces"] = [
        build_effect("surface", SURFACES, {"name": name, **settings})
        for name, settings in preset.get("surface", {}).items()
    ]
    if seed is not None:
        fields["seed"] = seed
    return Recipe(**fields)


def _load(name_or_path: str, base_dir: Path, seen: tuple[str, ...]) -> dict:
    text, source, here = _read(name_or_path, base_dir)
    if source in seen:
        raise ValueError(f"preset {name_or_path!r} extends itself")
    data = tomllib.loads(text)
    _check(data, name_or_path)
    if base := data.pop("extends", None):
        parent = _load(base, here, (*seen, source))
        parent.pop("description", None)  # each preset describes itself
        data = _merge(parent, data)
    return data


def _read(name_or_path: str, base_dir: Path) -> tuple[str, str, Path]:
    """The preset's text, a key identifying it, and the directory its own
    ``extends`` paths are relative to."""
    if name_or_path.endswith(".toml") or "/" in name_or_path:
        path = (base_dir / name_or_path).resolve()
        if not path.is_file():
            raise ValueError(f"no preset file {path}")
        return path.read_text(), str(path), path.parent
    builtin = _BUILTINS / f"{name_or_path}.toml"
    if not builtin.is_file():
        raise ValueError(
            f"unknown preset {name_or_path!r}; built-ins are "
            f"{', '.join(builtin_presets())}, or pass a .toml path"
        )
    return builtin.read_text(), f"builtin:{name_or_path}", base_dir


def _check(data: dict, name: str) -> None:
    if "seed" in data:
        raise ValueError(f"preset {name!r} sets a seed; presets never fix the seed")
    if unknown := data.keys() - PRESET_KEYS:
        raise ValueError(
            f"preset {name!r} has unknown key {', '.join(map(repr, sorted(unknown)))}"
        )


def _merge(base: dict, override: dict) -> dict:
    """``override`` deep-merged over ``base``; neither is modified."""
    merged = dict(base)
    for key, value in override.items():
        if isinstance(value, dict) and isinstance(merged.get(key), dict):
            merged[key] = _merge(merged[key], value)
        else:
            merged[key] = value
    return merged

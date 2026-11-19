"""Recipes: everything needed to render an image again exactly.

A ``Recipe`` names the shape, colour, size, padding, background, each effect
with its settings, and the seed. ``render(recipe)`` turns it into pixels, and
``save`` writes the recipe into the image file as JSON so every image carries
its own recipe::

    recipe = Recipe("face", "primary", 2160, prints=[Screenprint(ink=0.6)])
    save(render(recipe), recipe, "face.png")
    read_recipe("face.png") == recipe  # True
"""

import json
import random
from collections.abc import Sequence
from dataclasses import KW_ONLY, asdict, dataclass, field, fields
from importlib.metadata import version
from pathlib import Path
from typing import Any

from PIL import Image
from PIL.PngImagePlugin import PngInfo

from nltl_image.prints import PRINTS, Print
from nltl_image.surfaces import SURFACES, Surface

DEFAULT_SIZE = 2160  # 4K video frame height
SEED_LIMIT = 1_000_000  # seeds stay short enough to read and type
RECIPE_KEY = "nltl-recipe"  # PNG text chunk name
JPEG_SUFFIXES = {".jpg", ".jpeg"}

type Effect = Print | Surface


def new_seed() -> int:
    return random.randrange(SEED_LIMIT)


@dataclass(frozen=True)
class Recipe:
    shape: str = "face"
    color: str = "primary"
    size: int = DEFAULT_SIZE
    _: KW_ONLY
    padding: int = 0
    background: str | None = None
    # Any sequence is accepted; __post_init__ stores a tuple.
    prints: Sequence[Print] = ()
    surfaces: Sequence[Surface] = ()
    seed: int = field(default_factory=new_seed)

    def __post_init__(self) -> None:
        # Accept any sequence of effects but store tuples, so recipes stay
        # immutable and compare equal however they were built.
        object.__setattr__(self, "prints", tuple(self.prints))
        object.__setattr__(self, "surfaces", tuple(self.surfaces))

    def rng(self, kind: str, index: int, effect: Effect) -> random.Random:
        """The random stream for one effect.

        Each effect's stream depends only on the seed and the effect's place,
        so adding or removing one effect never changes what another does.
        """
        return random.Random(f"{self.seed}:{kind}:{index}:{effect.name}")

    def to_dict(self) -> dict[str, Any]:
        data = {f.name: getattr(self, f.name) for f in fields(self)}
        data["prints"] = [_effect_to_dict(e) for e in self.prints]
        data["surfaces"] = [_effect_to_dict(e) for e in self.surfaces]
        return {**data, "version": version("nltl-image-gen")}

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Recipe:
        data = {k: v for k, v in data.items() if k != "version"}
        data["prints"] = [
            build_effect("print", PRINTS, e) for e in data.get("prints", ())
        ]
        data["surfaces"] = [
            build_effect("surface", SURFACES, e) for e in data.get("surfaces", ())
        ]
        return cls(**data)

    def to_json(self) -> str:
        return json.dumps(self.to_dict())

    @classmethod
    def from_json(cls, text: str) -> Recipe:
        return cls.from_dict(json.loads(text))


def _effect_to_dict(effect: Effect) -> dict[str, Any]:
    return {"name": effect.name, **asdict(effect)}


def build_effect[T: Effect](kind: str, registry: dict[str, type[T]], data: dict) -> T:
    """Construct an effect from ``{"name": ..., **settings}``.

    Raises ``ValueError`` for an unknown name, an unknown setting, or a
    setting out of range.
    """
    settings = dict(data)
    name = settings.pop("name")
    if name not in registry:
        raise ValueError(
            f"unknown {kind} {name!r}; choose from {', '.join(sorted(registry))}"
        )
    known = {f.name for f in fields(registry[name])}
    if unknown := settings.keys() - known:
        raise ValueError(
            f"{name} has no setting {', '.join(sorted(unknown))}; "
            f"it has {', '.join(sorted(known))}"
        )
    return registry[name](**settings)


def save(image: Image.Image, recipe: Recipe, path: str | Path) -> None:
    """Save ``image`` with ``recipe`` embedded: a PNG text chunk, or the
    JPEG comment. JPEG has no transparency, so it needs a background."""
    path = Path(path)
    if path.suffix.lower() in JPEG_SUFFIXES:
        if not recipe.background:
            raise ValueError("JPEG has no transparency; pass a background")
        image.convert("RGB").save(path, quality=95, comment=recipe.to_json())
    else:
        info = PngInfo()
        info.add_text(RECIPE_KEY, recipe.to_json())
        image.save(path, pnginfo=info)


def read_recipe(path: str | Path) -> Recipe:
    """The recipe embedded in an image written by ``save``."""
    with Image.open(path) as image:
        text = image.info.get(RECIPE_KEY) or image.info.get("comment")
    if not text:
        raise ValueError(f"{path} has no nltl recipe")
    if isinstance(text, bytes):
        text = text.decode()
    return Recipe.from_json(text)

import json

import pytest
from PIL import Image, ImageChops

from nltl_image import Canvas, Recipe, Screenprint, read_recipe, render, save

FULL = Recipe(
    "space",
    "secondary",
    300,
    padding=10,
    background="#FFFFFF",
    prints=[Screenprint(ink=0.6)],
    surfaces=[Canvas(depth=0.5)],
    seed=42,
)


def same(a, b):
    return ImageChops.difference(a, b).getbbox() is None


def test_every_recipe_has_a_seed():
    seeds = {Recipe().seed for _ in range(20)}
    assert all(0 <= s < 1_000_000 for s in seeds)
    assert len(seeds) > 1


def test_effects_are_stored_as_tuples():
    assert FULL.prints == (Screenprint(ink=0.6),)


def test_round_trips_through_json():
    assert Recipe.from_json(FULL.to_json()) == FULL


def test_json_names_each_effect_and_records_the_version():
    data = json.loads(FULL.to_json())
    assert data["prints"] == [
        {
            "name": "screenprint",
            "ink": 0.6,
            "pull": 270.0,
            "starve": 0.5,
            "scale": 0.12,
            "tension": 0.002,
        }
    ]
    assert "version" in data


@pytest.mark.parametrize(
    ("change", "message"),
    [
        ({"prints": [{"name": "woodcut"}]}, "unknown print 'woodcut'"),
        ({"surfaces": [{"name": "canvas", "grain": 1}]}, "canvas.*grain"),
        ({"surfaces": [{"name": "canvas", "depth": 3}]}, "depth must be"),
    ],
)
def test_rejects_bad_effects(change, message):
    data = {**json.loads(FULL.to_json()), **change}
    with pytest.raises(ValueError, match=message):
        Recipe.from_dict(data)


def test_same_recipe_renders_the_same_image():
    assert same(render(FULL), render(Recipe.from_json(FULL.to_json())))


def test_effects_get_independent_randomness():
    # Adding canvas must not change where the screenprint put its ink.
    printed = Recipe("face", size=200, prints=[Screenprint()], seed=1)
    both = Recipe("face", size=200, prints=[Screenprint()], surfaces=[Canvas()], seed=1)
    assert same(render(printed).getchannel("A"), render(both).getchannel("A"))


@pytest.mark.parametrize("suffix", [".png", ".jpg"])
def test_saved_images_carry_their_recipe(tmp_path, suffix):
    path = tmp_path / f"out{suffix}"
    save(render(FULL), FULL, path)
    assert read_recipe(path) == FULL


def test_jpeg_needs_a_background(tmp_path):
    recipe = Recipe(size=64)
    with pytest.raises(ValueError, match="background"):
        save(render(recipe), recipe, tmp_path / "out.jpg")


def test_read_recipe_reports_images_without_one(tmp_path):
    path = tmp_path / "plain.png"
    Image.new("RGB", (4, 4)).save(path)
    with pytest.raises(ValueError, match="no nltl recipe"):
        read_recipe(path)

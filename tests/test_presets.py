import pytest

from nltl_image import (
    Canvas,
    Recipe,
    Screenprint,
    builtin_presets,
    load_preset,
    preset_recipe,
)


def write(tmp_path, name, text):
    path = tmp_path / name
    path.write_text(text)
    return path


def test_builtins_have_descriptions():
    presets = builtin_presets()
    assert {"flat", "poster", "worn", "canvas-print"} <= presets.keys()
    assert all(presets.values())


def test_flat_has_no_effects():
    recipe = preset_recipe(load_preset("flat"))
    assert recipe.prints == recipe.surfaces == ()


def test_worn_overrides_its_base():
    poster = preset_recipe(load_preset("poster")).prints[0]
    worn = preset_recipe(load_preset("worn")).prints[0]
    assert isinstance(worn, Screenprint)
    assert worn.ink < poster.ink
    assert worn.starve > poster.starve


def test_canvas_print_adds_a_surface_to_its_base():
    recipe = preset_recipe(load_preset("canvas-print"))
    assert recipe.prints == preset_recipe(load_preset("poster")).prints
    assert isinstance(recipe.surfaces[0], Canvas)


def test_description_is_not_inherited(tmp_path):
    path = write(tmp_path, "mine.toml", 'extends = "poster"\n')
    assert "description" not in load_preset(str(path))


def test_files_can_extend_builtins_and_other_files(tmp_path):
    write(tmp_path, "base.toml", 'extends = "poster"\n[surface.canvas]\ndepth = 0.2\n')
    path = write(tmp_path, "top.toml", 'extends = "base.toml"\nbackground = "#FFF"\n')
    recipe = preset_recipe(load_preset(str(path)))
    assert recipe.background == "#FFF"
    assert recipe.surfaces == (Canvas(depth=0.2),)
    assert recipe.prints == preset_recipe(load_preset("poster")).prints


def test_preset_recipe_takes_a_seed():
    assert preset_recipe(load_preset("flat"), seed=7).seed == 7


@pytest.mark.parametrize(
    ("text", "message"),
    [
        ("seed = 3\n", "seed"),
        ('colour = "primary"\n', "unknown key 'colour'"),
        ("[print.woodcut]\n", "unknown print 'woodcut'"),
        ("[surface.canvas]\ngrain = 1\n", "grain"),
    ],
)
def test_rejects_bad_presets(tmp_path, text, message):
    path = write(tmp_path, "bad.toml", text)
    with pytest.raises(ValueError, match=message):
        preset_recipe(load_preset(str(path)))


def test_rejects_cycles(tmp_path):
    write(tmp_path, "a.toml", 'extends = "b.toml"\n')
    write(tmp_path, "b.toml", 'extends = "a.toml"\n')
    with pytest.raises(ValueError, match="extends itself"):
        load_preset(str(tmp_path / "a.toml"))


def test_unknown_name_lists_builtins():
    with pytest.raises(ValueError, match="poster"):
        load_preset("nope")


def test_recipe_fields_pass_through():
    assert isinstance(preset_recipe({"size": 100}), Recipe)
    assert preset_recipe({"size": 100}).size == 100

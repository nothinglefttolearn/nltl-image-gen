import re

import pytest
from PIL import Image

from nltl_image import Canvas, Screenprint, read_recipe
from nltl_image.cli import OUTPUT_DIR_ENV, build_parser, main


def run(tmp_path, *args, name="out.png"):
    out = tmp_path / name
    main(["--size", "64", "--output", str(out), *args])
    return read_recipe(out)


def usage_error(capsys, *args):
    with pytest.raises(SystemExit) as exc:
        main(["--size", "64", *args])
    assert exc.value.code == 2
    return capsys.readouterr().err


def test_writes_png_with_recipe(tmp_path):
    recipe = run(tmp_path, "--shape", "space", "--seed", "3")
    assert (recipe.shape, recipe.size, recipe.seed) == ("space", 64, 3)
    assert Image.open(tmp_path / "out.png").mode == "RGBA"


def test_writes_jpeg_with_background(tmp_path):
    run(tmp_path, "--background", "#FFFFFF", name="out.jpg")
    assert Image.open(tmp_path / "out.jpg").format == "JPEG"


def test_rejects_jpeg_without_background(tmp_path, capsys):
    err = usage_error(capsys, "--output", str(tmp_path / "face.jpg"))
    assert "background" in err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--padding", "32"], "padding must be"),
        (["--background", "notacolour"], "unknown color specifier"),
        (["--print", "screenprint", "--ink", "2"], "ink must be"),
        (["--ink", "0.5"], "--ink needs --print screenprint"),
        (["--depth", "0.5"], "--depth needs --surface canvas"),
        (["--preset", "nope"], "unknown preset"),
    ],
)
def test_reports_bad_values_as_usage_errors(args, message, capsys, tmp_path):
    assert message in usage_error(capsys, "--output", str(tmp_path / "x.png"), *args)


def test_print_and_surface_are_independent(tmp_path):
    assert run(tmp_path, "--print", "screenprint").surfaces == ()
    assert run(tmp_path, "--surface", "canvas").prints == ()
    both = run(tmp_path, "--print", "screenprint", "--surface", "canvas")
    assert both.prints == (Screenprint(),) and both.surfaces == (Canvas(),)


def test_options_adjust_their_effect(tmp_path):
    recipe = run(
        tmp_path, "--print", "screenprint", "--ink", "0.4", "--pull", "90",
        "--surface", "canvas", "--weave", "0.01", "--depth", "0.5",
    )  # fmt: skip
    assert recipe.prints == (Screenprint(ink=0.4, pull=90),)
    assert recipe.surfaces == (Canvas(weave=0.01, depth=0.5),)


def test_options_override_a_preset(tmp_path):
    recipe = run(tmp_path, "--preset", "canvas-print", "--ink", "0.4")
    assert recipe.prints[0].ink == 0.4
    assert recipe.prints[0].starve == 0.3  # still from the preset
    assert recipe.surfaces


def test_none_drops_an_effect_from_a_preset(tmp_path):
    recipe = run(tmp_path, "--preset", "canvas-print", "--surface", "none")
    assert recipe.prints and recipe.surfaces == ()


def test_choosing_an_active_effect_keeps_preset_settings(tmp_path):
    recipe = run(tmp_path, "--preset", "worn", "--print", "screenprint")
    assert recipe.prints[0].ink == 0.5


def test_default_name_has_preset_and_seed(tmp_path, monkeypatch, capsys):
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv(OUTPUT_DIR_ENV, raising=False)
    main(["--size", "64", "--preset", "worn", "--seed", "123"])
    (path,) = (tmp_path / "output").iterdir()
    assert re.fullmatch(r"nltl-face-primary-worn-\d{8}-\d{6}-s123\.png", path.name)
    assert "(seed 123)" in capsys.readouterr().out


def test_help_lists_builtin_presets():
    assert "canvas-print" in build_parser().format_help()


def test_output_dir_from_environment(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(OUTPUT_DIR_ENV, "renders/today")
    main(["--size", "64", "--seed", "1"])
    (path,) = (tmp_path / "renders" / "today").iterdir()
    assert path.name.startswith("nltl-face-primary-")
    assert not (tmp_path / "output").exists()


def test_output_dir_expands_home(tmp_path, monkeypatch):
    monkeypatch.setenv("HOME", str(tmp_path))
    monkeypatch.setenv(OUTPUT_DIR_ENV, "~/renders")
    main(["--size", "64"])
    assert len(list((tmp_path / "renders").iterdir())) == 1


def test_empty_output_dir_means_default(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setenv(OUTPUT_DIR_ENV, "")
    main(["--size", "64"])
    assert len(list((tmp_path / "output").iterdir())) == 1


def test_output_path_beats_environment(tmp_path, monkeypatch):
    monkeypatch.setenv(OUTPUT_DIR_ENV, str(tmp_path / "ignored"))
    run(tmp_path)
    assert (tmp_path / "out.png").exists() and not (tmp_path / "ignored").exists()


def test_color_choices_are_the_art_palette(capsys):
    assert "invalid choice" in usage_error(capsys, "--color", "accent")


def test_background_takes_a_palette_name(tmp_path):
    assert run(tmp_path, "--background", "canvas").background == "canvas"


def test_new_shape_variants(tmp_path):
    assert run(tmp_path, "--shape", "face3").shape == "face3"

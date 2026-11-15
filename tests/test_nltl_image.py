import pytest
from PIL import Image, ImageChops

from nltl_image import main, render

SIZE = 1000


def alpha(shape: str, padding: int) -> Image.Image:
    return render(shape, "primary", SIZE, padding).getchannel("A")


@pytest.mark.parametrize("padding", [0, 1, 100, 333])
def test_padding_is_equal_on_every_side(padding):
    # space touches all four sides of the unit square, so its bounding box is
    # exactly the inner square.
    assert alpha("space", padding).getbbox() == (
        padding,
        padding,
        SIZE - padding,
        SIZE - padding,
    )


@pytest.mark.parametrize("padding", [0, 100])
def test_face_and_space_tile_the_inner_square(padding):
    union = ImageChops.lighter(alpha("face", padding), alpha("space", padding))
    inner = union.crop((padding, padding, SIZE - padding, SIZE - padding))
    assert inner.getextrema() == (255, 255), "gap between face and space"
    assert union.getbbox() == (padding, padding, SIZE - padding, SIZE - padding)


def test_background_defaults_to_transparent():
    assert render("face", "primary", SIZE).getpixel((SIZE - 1, 0)) == (0, 0, 0, 0)


def test_fill_uses_named_colour():
    assert render("face", "secondary", SIZE).getpixel((0, SIZE - 1)) == (
        0x87,
        0x9B,
        0x87,
        255,
    )


@pytest.mark.parametrize("padding", [-1, SIZE // 2])
def test_render_rejects_out_of_range_padding(padding):
    with pytest.raises(ValueError, match="padding"):
        render("face", "primary", SIZE, padding)


def test_cli_writes_png(tmp_path):
    out = tmp_path / "face.png"
    main(["--size", "64", "--output", str(out)])
    assert Image.open(out).mode == "RGBA"


def test_cli_rejects_jpeg_without_background(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--size", "64", "--output", str(tmp_path / "face.jpg")])
    assert exc.value.code == 2
    assert "pass --background" in capsys.readouterr().err


def test_cli_reports_bad_padding_as_usage_error(capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--size", "64", "--padding", "32"])
    assert exc.value.code == 2
    assert "padding must be" in capsys.readouterr().err

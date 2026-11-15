import pytest
from PIL import Image

from nltl_image.cli import main


def test_writes_png(tmp_path):
    out = tmp_path / "face.png"
    main(["--size", "64", "--output", str(out)])
    assert Image.open(out).mode == "RGBA"


def test_writes_jpeg_with_background(tmp_path):
    out = tmp_path / "face.jpg"
    main(["--size", "64", "--background", "#FFFFFF", "--output", str(out)])
    assert Image.open(out).format == "JPEG"


def test_rejects_jpeg_without_background(tmp_path, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--size", "64", "--output", str(tmp_path / "face.jpg")])
    assert exc.value.code == 2
    assert "pass --background" in capsys.readouterr().err


@pytest.mark.parametrize(
    ("args", "message"),
    [
        (["--padding", "32"], "padding must be"),
        (["--background", "notacolour"], "unknown color specifier"),
    ],
)
def test_reports_bad_values_as_usage_errors(args, message, capsys):
    with pytest.raises(SystemExit) as exc:
        main(["--size", "64", *args])
    assert exc.value.code == 2
    assert message in capsys.readouterr().err

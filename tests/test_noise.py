import random

import pytest
from PIL import ImageChops

from nltl_image.noise import fractal_noise, linear_ramp

SIZE = 256


def test_same_seed_gives_same_noise():
    a = fractal_noise(SIZE, 0.2, random.Random(1))
    b = fractal_noise(SIZE, 0.2, random.Random(1))
    assert ImageChops.difference(a, b).getbbox() is None


def test_different_seeds_give_different_noise():
    a = fractal_noise(SIZE, 0.2, random.Random(1))
    b = fractal_noise(SIZE, 0.2, random.Random(2))
    assert ImageChops.difference(a, b).getbbox() is not None


@pytest.mark.parametrize("angle", [0, 30, 90])
def test_noise_is_square_and_equalised(angle):
    field = fractal_noise(SIZE, 0.2, random.Random(0), angle=angle)
    assert field.size == (SIZE, SIZE)
    # Equalised: about half the pixels fall below the midpoint.
    below = sum(field.histogram()[:128]) / SIZE**2
    assert 0.4 < below < 0.6


@pytest.mark.parametrize(
    ("angle", "low", "high"),
    [
        (0, (0, SIZE // 2), (SIZE - 1, SIZE // 2)),  # rises rightward
        (270, (SIZE // 2, 0), (SIZE // 2, SIZE - 1)),  # rises downward
    ],
)
def test_ramp_rises_along_angle(angle, low, high):
    ramp = linear_ramp(SIZE, angle)
    assert ramp.getpixel(low) < 20
    assert ramp.getpixel(high) > 235

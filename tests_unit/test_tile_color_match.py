"""Unit tests for the per-tile color/brightness match (fork addition).

Self-contained: loads ``modules/tile_color.py`` directly by file path, so it needs
no ComfyUI engine, no models, and no GPU. Run them with:

    python -m pytest tests_unit/

They live outside ``test/`` on purpose — that directory's conftest bootstraps
ComfyUI and downloads checkpoints, which this feature doesn't need.
"""

import importlib.util
import os

import numpy as np
import pytest
from PIL import Image

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))


def _load_tile_color():
    """Load modules/tile_color.py in isolation (only PIL/numpy/color-matcher)."""
    path = os.path.join(REPO_ROOT, "modules", "tile_color.py")
    spec = importlib.util.spec_from_file_location("usdu_tile_color_under_test", path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


tc = _load_tile_color()
match_tile_color = tc.match_tile_color
TILE_COLOR_MATCH_METHODS = tc.TILE_COLOR_MATCH_METHODS

_HAS_COLOR_MATCHER = importlib.util.find_spec("color_matcher") is not None
needs_lib = pytest.mark.skipif(not _HAS_COLOR_MATCHER, reason="color-matcher not installed")


@pytest.fixture
def ref_and_drifted():
    """A reference image and a copy shifted in brightness/color ('drifted')."""
    rng = np.random.default_rng(0)
    base = (rng.random((48, 48, 3)) * 120 + 60).astype("uint8")
    ref = Image.fromarray(base, "RGB")
    drift = np.clip(base.astype(int) + np.array([40, 15, -20]), 0, 255).astype("uint8")
    tile = Image.fromarray(drift, "RGB")
    return ref, tile


def _mean_abs(img_a, img_b):
    return float(np.abs(np.asarray(img_a, float) - np.asarray(img_b, float)).mean())


def test_off_is_a_noop_and_returns_same_object(ref_and_drifted):
    ref, tile = ref_and_drifted
    assert match_tile_color(tile, ref, "off", 1.0) is tile


def test_zero_strength_is_a_noop(ref_and_drifted):
    ref, tile = ref_and_drifted
    assert match_tile_color(tile, ref, "mkl", 0.0) is tile


def test_methods_list_well_formed():
    assert TILE_COLOR_MATCH_METHODS[0] == "off"
    assert "mkl" in TILE_COLOR_MATCH_METHODS


def test_unknown_method_falls_back_to_original(ref_and_drifted):
    # color-matcher raises on an unknown method; helper must not crash.
    ref, tile = ref_and_drifted
    out = match_tile_color(tile, ref, "not-a-real-method", 1.0)
    assert _mean_abs(out, tile) == 0.0


@needs_lib
def test_mkl_removes_linear_drift(ref_and_drifted):
    ref, tile = ref_and_drifted
    before = _mean_abs(tile, ref)
    out = match_tile_color(tile, ref, "mkl", 1.0)
    after = _mean_abs(out, ref)
    assert out.size == tile.size
    assert before > 10.0  # the drift is real
    assert after < 1.0    # MKL fully corrects a linear shift


@needs_lib
def test_strength_blends_between_tile_and_full_match(ref_and_drifted):
    ref, tile = ref_and_drifted
    full = match_tile_color(tile, ref, "mkl", 1.0)
    half = match_tile_color(tile, ref, "mkl", 0.5)
    # half should sit between the original tile and the fully matched result
    assert _mean_abs(half, tile) > 0.0
    assert _mean_abs(half, tile) < _mean_abs(full, tile)


@needs_lib
@pytest.mark.parametrize("method", [m for m in TILE_COLOR_MATCH_METHODS if m != "off"])
def test_every_method_runs_and_preserves_shape(ref_and_drifted, method):
    ref, tile = ref_and_drifted
    out = match_tile_color(tile, ref, method, 1.0)
    assert out.size == tile.size
    assert out.mode == "RGB"
    # every method should move the tile at least somewhat toward the reference
    assert _mean_abs(out, ref) <= _mean_abs(tile, ref) + 1e-6

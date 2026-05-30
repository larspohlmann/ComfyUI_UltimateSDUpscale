"""Per-tile color/brightness match used by the USDU tiling loop (fork addition).

Kept deliberately dependency-light — only PIL, plus numpy and the optional
color-matcher library imported lazily inside the function — and separate from the
heavy ComfyUI imports in ``processing.py`` so it can be unit-tested in isolation
(see ``tests_unit/``). See the README's "About this fork" section.
"""

import logging

from PIL import Image

logger = logging.getLogger(__name__)

# Color-transfer methods exposed by the tile_color_match widget. "off" disables.
# Backed by the color-matcher library (the same one behind KJNodes' ColorMatch).
TILE_COLOR_MATCH_METHODS = ["off", "mkl", "reinhard", "hm", "mvgd", "hm-mkl-hm", "hm-mvgd-hm"]


def match_tile_color(tile, ref, method="mkl", strength=1.0):
    """Return *tile* (PIL) re-graded so its color distribution matches *ref* (PIL).

    Each redrawn tile is denoised independently, so tiles drift apart in
    brightness and color. Matching a tile to the SAME region of the (pre-redraw)
    upscaled canvas — which is globally consistent — removes that drift at the
    source while leaving the tile's new spatial detail untouched.

    method: one of TILE_COLOR_MATCH_METHODS; "off" disables.
    strength: 0..1 blend between the original tile and the fully matched result.
    Falls back to the original tile on any error so a redraw is never lost.
    """
    if method == "off" or strength <= 0:
        return tile
    if method not in TILE_COLOR_MATCH_METHODS:
        # Guard up front: color-matcher raises a bare BaseException on an
        # unknown method, which a normal `except Exception` would not catch.
        logger.warning(f"USDU tile color match: unknown method {method!r}, skipping")
        return tile
    try:
        import numpy as np
        from color_matcher import ColorMatcher
        tile_np = np.asarray(tile.convert("RGB"), dtype=np.float32) / 255.0
        ref_np = np.asarray(ref.convert("RGB"), dtype=np.float32) / 255.0
        result = ColorMatcher().transfer(src=tile_np, ref=ref_np, method=method)
        if strength != 1.0:
            result = tile_np + strength * (result - tile_np)
        result = np.clip(result * 255.0 + 0.5, 0, 255).astype(np.uint8)
        return Image.fromarray(result, mode="RGB")
    except Exception as e:
        logger.warning(f"USDU tile color match failed (method={method}): {e}")
        return tile

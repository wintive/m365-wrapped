"""One combined image: the 9 stat cards laid out in a 3x3 grid (grid.png)."""

from __future__ import annotations

import base64
import tempfile
from pathlib import Path

from ..metrics.models import WrappedStats
from .cards import _logo_data_uri, _svg_for, rasterize

_COLS = 3
_CARD = 1080
_CW = 660          # rendered card size in the grid
_GAP = 30
_PAD = 50


def _card_png_b64(stats: WrappedStats, card, logo_href: str | None) -> str:
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        png = Path(f.name)
    try:
        rasterize(_svg_for(card, stats, logo_href), png, _CARD, _CARD)
        return base64.b64encode(png.read_bytes()).decode("ascii")
    finally:
        png.unlink(missing_ok=True)


def render_grid(stats: WrappedStats, out_dir: str, brand_logo: str | None = None) -> Path:
    """Render the first 9 cards as a single 3x3 image (out/grid.png)."""
    logo_href = _logo_data_uri(brand_logo)
    cards = stats.cards[:9]
    rows = (len(cards) + _COLS - 1) // _COLS
    w = _PAD * 2 + _COLS * _CW + (_COLS - 1) * _GAP
    h = _PAD * 2 + rows * _CW + (rows - 1) * _GAP

    imgs = []
    for i, c in enumerate(cards):
        x = _PAD + (i % _COLS) * (_CW + _GAP)
        y = _PAD + (i // _COLS) * (_CW + _GAP)
        b64 = _card_png_b64(stats, c, logo_href)
        imgs.append(
            f'<image href="data:image/png;base64,{b64}" x="{x}" y="{y}" '
            f'width="{_CW}" height="{_CW}"/>'
        )
    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" '
        f'viewBox="0 0 {w} {h}"><rect width="{w}" height="{h}" fill="#0b1220"/>'
        f'{"".join(imgs)}</svg>'
    )
    png = Path(out_dir) / "grid.png"
    png.parent.mkdir(parents=True, exist_ok=True)
    rasterize(svg, png, w, h)
    return png

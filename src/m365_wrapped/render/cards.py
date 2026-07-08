from __future__ import annotations

import base64
import mimetypes
import shutil
import subprocess
import tempfile
from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from ..metrics.models import WrappedStats
from .theme import icon_for, theme_for, value_size

_PERIOD_LABEL = {"D7": "LAST 7 DAYS", "D30": "LAST 30 DAYS",
                 "D90": "LAST 90 DAYS", "D180": "LAST 180 DAYS"}


def _human_period(period: str) -> str:
    return _PERIOD_LABEL.get(period, period)


_EYEBROW_MAX_W = 968.0  # px available between the card's side padding


def _eyebrow_attrs(text: str, fs: float = 30.0, ls: float = 7.0) -> dict:
    """Scale the eyebrow so a long tenant name never overflows/clips the card."""
    est = len(text) * (fs * 0.60 + ls)
    if est <= _EYEBROW_MAX_W:
        return {"eyebrow_size": fs, "eyebrow_ls": ls, "eyebrow_textlength": None}
    s = _EYEBROW_MAX_W / est
    return {
        "eyebrow_size": round(fs * s, 1),
        "eyebrow_ls": round(ls * s, 2),
        "eyebrow_textlength": int(_EYEBROW_MAX_W),  # hard cap, belt-and-suspenders
    }


_env = Environment(
    loader=PackageLoader("m365_wrapped.render", "templates"),
    autoescape=select_autoescape(enabled_extensions=("html", "htm", "xml", "svg", "j2")),
)


def _logo_data_uri(path: str | None) -> str | None:
    """Embed an MSP/client logo as a data URI (self-contained SVG)."""
    if not path:
        return None
    p = Path(path)
    if not p.is_file():
        return None
    mime = mimetypes.guess_type(p.name)[0] or "image/png"
    b64 = base64.b64encode(p.read_bytes()).decode("ascii")
    return f"data:{mime};base64,{b64}"


def _svg_for(card, stats: WrappedStats, logo_href: str | None) -> str:
    accent, accent_dark, accent_tint = theme_for(card.key)
    eyebrow = f"{stats.tenant_label.upper()}  ·  M365 WRAPPED  ·  {_human_period(stats.period)}"
    tmpl = _env.get_template("card.svg.j2")
    return tmpl.render(
        card=card,
        eyebrow=eyebrow,
        **_eyebrow_attrs(eyebrow),
        footer="by Wintive · wintive.com",
        accent=accent,
        accent_dark=accent_dark,
        accent_tint=accent_tint,
        icon=icon_for(card.key),
        value_size=value_size(card.value),
        value_y=606,
        title_y=706,
        pill_y=792,
        pill_w=max(240, len(card.subtitle) * 22 + 96),
        logo_href=logo_href,
    )


def rasterize(svg: str, png: Path, width: int = 1080, height: int = 1080) -> None:
    exe = shutil.which("rsvg-convert")
    if not exe:
        raise RuntimeError(
            "rsvg-convert not found. Install librsvg (Debian/Ubuntu: 'apt-get install "
            "librsvg2-bin', macOS: 'brew install librsvg'). The Docker image ships it."
        )
    with tempfile.NamedTemporaryFile("w", suffix=".svg", encoding="utf-8", delete=False) as f:
        f.write(svg)
        src = f.name
    try:
        subprocess.run(
            [exe, "-w", str(width), "-h", str(height), "-o", str(png), src],
            check=True, capture_output=True,
        )
    finally:
        Path(src).unlink(missing_ok=True)


def render_cards(stats: WrappedStats, out_dir: str, brand_logo: str | None = None) -> list[Path]:
    """Render one square 1080x1080 PNG per stat (SVG -> rsvg-convert, no browser)."""
    cards_dir = Path(out_dir) / "cards"
    cards_dir.mkdir(parents=True, exist_ok=True)
    logo_href = _logo_data_uri(brand_logo)
    paths: list[Path] = []
    for card in stats.cards:
        png = cards_dir / f"{card.key}.png"
        rasterize(_svg_for(card, stats, logo_href), png)
        paths.append(png)
    return paths


def render_card_svg(stats: WrappedStats, card, brand_logo: str | None = None) -> str:
    """Expose the raw SVG for a single card (used to compose the README hero)."""
    return _svg_for(card, stats, _logo_data_uri(brand_logo))

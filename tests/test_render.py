import shutil

import pytest

from m365_wrapped.demo import demo_bundle
from m365_wrapped.metrics.aggregate import build_stats
from m365_wrapped.render.cards import _eyebrow_attrs, render_card_svg, render_cards
from m365_wrapped.render.html import render_page
from m365_wrapped.render.grid import render_grid


@pytest.mark.skipif(shutil.which("rsvg-convert") is None, reason="librsvg not installed")
def test_render_grid_writes_3x3_png(tmp_path) -> None:
    p = render_grid(build_stats(demo_bundle(), "D180"), str(tmp_path))
    assert p.name == "grid.png" and p.stat().st_size > 5000
    assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"


def test_eyebrow_autofits_long_tenant() -> None:
    short = _eyebrow_attrs("CONTOSO · M365 WRAPPED · LAST 7 DAYS")
    assert short["eyebrow_textlength"] is None          # short label: untouched
    long = _eyebrow_attrs("A VERY LONG ORGANIZATION NAME INC · M365 WRAPPED · LAST 180 DAYS")
    assert long["eyebrow_textlength"] == 968            # long label: hard-capped
    assert long["eyebrow_size"] < short["eyebrow_size"]  # and scaled down


def test_card_svg_is_wellformed_and_escaped() -> None:
    # A tenant label with markup must be escaped, not injected into the SVG.
    stats = build_stats(demo_bundle(), "D180", tenant_label="<b>&z")
    svg = render_card_svg(stats, stats.cards[0])
    assert svg.lstrip().startswith("<svg")
    assert "<B>" not in svg and "<b>" not in svg  # eyebrow upper-cases the label
    assert "&lt;B&gt;" in svg and "&amp;Z" in svg


def test_html_page_lists_every_card() -> None:
    stats = build_stats(demo_bundle(), "D180")
    import tempfile

    with tempfile.TemporaryDirectory() as d:
        page = render_page(stats, d)
        html = page.read_text()
    for card in stats.cards:
        assert f"cards/{card.key}.png" in html


@pytest.mark.skipif(shutil.which("rsvg-convert") is None, reason="librsvg not installed")
def test_render_cards_writes_png(tmp_path) -> None:
    stats = build_stats(demo_bundle(), "D180")
    paths = render_cards(stats, str(tmp_path))
    assert len(paths) == len(stats.cards)
    for p in paths:
        assert p.exists() and p.stat().st_size > 1000
        assert p.read_bytes()[:8] == b"\x89PNG\r\n\x1a\n"

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer

from .config import Settings, load_settings
from .metrics.models import WrappedStats

app = typer.Typer(add_completion=False, help="Spotify Wrapped, but for your Microsoft 365 tenant.")


def _collect(settings: Settings, period: str) -> WrappedStats:
    from .auth import get_token
    from .graph.client import GraphClient
    from .graph.reports import collect_all
    from .metrics.aggregate import build_stats

    token = get_token(settings)
    with GraphClient(token) as c:
        bundle = collect_all(c, period)
    return build_stats(bundle, period)


@app.command()
def collect(
    period: Optional[str] = typer.Option(None, help="D7 | D30 | D90 | D180"),
    out: Optional[str] = typer.Option(None),
) -> None:
    """Fetch usage from Graph and write stats.json."""
    from .output import write_stats

    s = load_settings()
    stats = _collect(s, period or s.period)
    p = write_stats(stats, out or s.out_dir)
    typer.echo(f"Wrote {p} ({len(stats.cards)} cards)")


@app.command()
def render(
    stats: str = typer.Option("out/stats.json"),
    out: Optional[str] = typer.Option(None),
) -> None:
    """Render cards + index.html from a stats.json."""
    from .render.cards import render_cards
    from .render.html import render_page

    ws = WrappedStats(**json.loads(Path(stats).read_text()))
    out_dir = out or str(Path(stats).parent)
    render_cards(ws, out_dir)
    render_page(ws, out_dir)
    typer.echo(f"Rendered {len(ws.cards)} cards to {out_dir}")


@app.command()
def run(
    period: Optional[str] = typer.Option(None),
    out: Optional[str] = typer.Option(None),
    anonymize: bool = typer.Option(False),
    tenant: Optional[str] = typer.Option(None, help="label shown on the cards (e.g. your org name)"),
) -> None:
    """collect + render in one shot."""
    from .output import write_stats
    from .render.cards import render_cards
    from .render.grid import render_grid
    from .render.html import render_page

    s = load_settings()
    stats = _collect(s, period or s.period)
    if tenant:
        stats.tenant_label = tenant
    if anonymize or s.anonymize:
        stats.tenant_label = "A Microsoft 365 tenant"
    out_dir = out or s.out_dir
    write_stats(stats, out_dir)
    render_cards(stats, out_dir, brand_logo=s.brand_logo)
    render_grid(stats, out_dir, brand_logo=s.brand_logo)
    render_page(stats, out_dir)
    typer.echo(f"Done -> {out_dir}: grid.png (3x3) + {len(stats.cards)} cards + index.html")


@app.command()
def demo(
    out: Optional[str] = typer.Option(None, help="output dir (default ./out)"),
    brand_logo: Optional[str] = typer.Option(None, help="optional MSP/client logo (PNG/SVG)"),
    tenant: str = typer.Option("Contoso", help="label shown on the cards"),
) -> None:
    """Generate a full card set from synthetic data — no Azure, no login. Try it in 10s."""
    from .demo import demo_bundle
    from .metrics.aggregate import build_stats
    from .output import write_stats
    from .render.cards import render_cards
    from .render.grid import render_grid
    from .render.html import render_page

    stats = build_stats(demo_bundle(), "D180", tenant_label=tenant)
    out_dir = out or "./out"
    write_stats(stats, out_dir)
    render_cards(stats, out_dir, brand_logo=brand_logo)
    render_grid(stats, out_dir, brand_logo=brand_logo)
    render_page(stats, out_dir)
    typer.echo(f"Demo -> {out_dir}: grid.png (3x3) + {len(stats.cards)} cards + index.html")

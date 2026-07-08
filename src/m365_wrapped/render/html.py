from __future__ import annotations

from pathlib import Path

from jinja2 import Environment, PackageLoader, select_autoescape

from ..metrics.models import WrappedStats

_env = Environment(
    loader=PackageLoader("m365_wrapped.render", "templates"),
    autoescape=select_autoescape(enabled_extensions=("html", "htm", "xml", "svg", "j2")),
)


def render_page(stats: WrappedStats, out_dir: str) -> Path:
    tmpl = _env.get_template("page.html.j2")
    out = Path(out_dir) / "index.html"
    out.write_text(tmpl.render(stats=stats), encoding="utf-8")
    return out

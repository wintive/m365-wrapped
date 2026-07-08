from __future__ import annotations

from pathlib import Path

from .metrics.models import WrappedStats


def write_stats(stats: WrappedStats, out_dir: str) -> Path:
    Path(out_dir).mkdir(parents=True, exist_ok=True)
    p = Path(out_dir) / "stats.json"
    p.write_text(stats.model_dump_json(indent=2, exclude={"raw"}), encoding="utf-8")
    return p

"""Per-stat visual theme: accent palette + hand-drawn vector icons (no emoji).

The visual IS the product, so cards are rendered from SVG (crisp, deterministic,
no headless browser). Icons are stroke paths drawn in a ~[-72,72] box centred on
the origin; the template translates + strokes them in the accent tint.
"""

from __future__ import annotations

# key -> (accent, accent_dark [bg bottom], accent_tint [icon/value/text])
PALETTE: dict[str, tuple[str, str, str]] = {
    "email":    ("#5B8DEF", "#141F38", "#C4D8FF"),
    "meetings": ("#B980F0", "#20183A", "#E6CFFF"),
    "hours":    ("#7C6BF0", "#1A1740", "#D6CEFF"),
    "chat":     ("#59D3C4", "#0E2A28", "#C2F3EC"),
    "docs_shared": ("#8B95F0", "#191C3A", "#D2D7FF"),
    "storage":  ("#3FB0BC", "#0E2A2E", "#BCEDF2"),
    "files":    ("#F0A868", "#2E2008", "#FBD9B0"),
    "top_app":  ("#F2B705", "#2C2408", "#FFE6A0"),
    "busiest":  ("#FF6B6B", "#331616", "#FFC9C9"),
    "quietest": ("#3DD68C", "#0F2A20", "#BFF3D9"),
    "active":   ("#4EC1E0", "#0E2830", "#BEEEF7"),
}
_DEFAULT = ("#3FB0BC", "#0E2A2E", "#BCEDF2")

# Stroke-path icons (drawn in a ~144x144 box centred on 0,0).
ICONS: dict[str, str] = {
    "email": (
        '<rect x="-74" y="-52" width="148" height="104" rx="18"/>'
        '<path d="M-74 -42 L0 16 L74 -42"/>'
    ),
    "meetings": (
        '<rect x="-70" y="-54" width="140" height="116" rx="18"/>'
        '<path d="M-70 -18 H70"/><path d="M-38 -76 V-42"/><path d="M38 -76 V-42"/>'
        '<path d="M-26 24 L-6 44 L34 0"/>'
    ),
    "hours": (
        '<circle cx="0" cy="0" r="70"/>'
        '<path d="M0 -40 V4 L34 26"/>'
    ),
    "storage": (
        '<ellipse cx="0" cy="-56" rx="60" ry="20"/>'
        '<path d="M-60 -56 V56 C-60 76 60 76 60 56 V-56"/>'
        '<path d="M-60 0 C-60 20 60 20 60 0"/>'
    ),
    "top_app": (
        '<path d="M-46 -60 H46 V-32 C46 8 -46 8 -46 -32 Z"/>'
        '<path d="M-46 -50 C-84 -50 -84 -4 -50 -4"/>'
        '<path d="M46 -50 C84 -50 84 -4 50 -4"/>'
        '<path d="M0 8 V56"/><path d="M-34 68 H34"/>'
    ),
    "busiest": (
        '<path d="M6 -74 C44 -30 64 -14 40 36 C28 62 -28 62 -40 36 '
        'C-54 6 -16 -6 -6 -32 C2 -50 -4 -62 6 -74 Z"/>'
        '<path d="M2 42 C-14 28 -6 6 8 0 C6 20 22 24 16 42 C12 56 -2 56 2 42 Z"/>'
    ),
    "quietest": (
        '<path d="M46 18 A58 58 0 1 1 -18 -46 A44 44 0 0 0 46 18 Z"/>'
        '<path d="M28 -44 L34 -30 L48 -24 L34 -18 L28 -4 L22 -18 L8 -24 L22 -30 Z"/>'
    ),
    "active": (
        '<circle cx="-2" cy="-30" r="30"/>'
        '<path d="M-56 60 C-56 18 52 18 52 60"/>'
    ),
    "chat": (
        '<rect x="-66" y="-54" width="132" height="90" rx="22"/>'
        '<path d="M-30 36 L-30 66 L4 36"/>'
        '<path d="M-34 -14 H34"/><path d="M-34 10 H14"/>'
    ),
    "files": (
        '<path d="M-44 -66 H20 L46 -40 V66 H-44 Z"/>'
        '<path d="M20 -66 V-40 H46"/>'
        '<path d="M-24 -6 H28"/><path d="M-24 22 H28"/>'
    ),
    "docs_shared": (
        '<circle cx="-44" cy="0" r="20"/><circle cx="42" cy="-42" r="20"/>'
        '<circle cx="42" cy="42" r="20"/>'
        '<path d="M-27 -9 L25 -34"/><path d="M-27 9 L25 34"/>'
    ),
}
_DEFAULT_ICON = '<path d="M10 -74 L-36 8 H2 L-10 74 L44 -14 H2 Z"/>'


def theme_for(key: str) -> tuple[str, str, str]:
    return PALETTE.get(key, _DEFAULT)


def icon_for(key: str) -> str:
    return ICONS.get(key, _DEFAULT_ICON)


def value_size(value: str) -> int:
    """Auto-fit the headline number/word so long values never overflow."""
    n = len(value)
    if n <= 3:
        return 264
    if n <= 5:
        return 216
    if n <= 7:
        return 176
    if n <= 10:
        return 132
    if n <= 14:
        return 102
    return 80

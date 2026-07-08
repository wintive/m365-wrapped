from __future__ import annotations

import re
from datetime import datetime, timezone

from .models import StatCard, WrappedStats

Rows = list[dict[str, str]]

_ISO_DUR = re.compile(
    r"^P(?:\d+D)?T?(?:(\d+)H)?(?:(\d+)M)?(?:(\d+(?:\.\d+)?)S)?$", re.IGNORECASE
)
_HOURS_PER_YEAR = 8760  # calendar hours (365d) — matches the "1.4 years" framing


def _to_int(s: object) -> int:
    try:
        return int(float(str(s)))
    except (TypeError, ValueError):
        return 0


def _sum(rows: Rows, col: str) -> int:
    return sum(_to_int(r.get(col, 0)) for r in rows)


def _latest_max(rows: Rows, col: str) -> int:
    vals = [_to_int(r.get(col, 0)) for r in rows]
    return max(vals) if vals else 0


def _fmt(n: int) -> str:
    return f"{n:,}"


def _fmt_bytes(n: float) -> str:
    for unit in ("B", "KB", "MB", "GB", "TB", "PB"):
        if n < 1024:
            return f"{n:.0f} {unit}" if unit in ("B", "KB") else f"{n:.1f} {unit}"
        n /= 1024
    return f"{n:.1f} EB"


def _duration_seconds(v: object) -> float:
    """Parse a Graph duration cell: ISO-8601 (PT1H2M3S), HH:MM:SS, or raw seconds."""
    s = str(v).strip()
    if not s:
        return 0.0
    m = _ISO_DUR.match(s)
    if m and any(m.groups()):
        h, mi, se = (float(g) if g else 0.0 for g in m.groups())
        return h * 3600 + mi * 60 + se
    if ":" in s:
        parts = s.split(":")
        try:
            nums = [float(p) for p in parts]
        except ValueError:
            return 0.0
        while len(nums) < 3:
            nums.insert(0, 0.0)
        return nums[0] * 3600 + nums[1] * 60 + nums[2]
    try:
        return float(s)  # raw seconds
    except ValueError:
        return 0.0


def _meeting_seconds(detail: Rows) -> float:
    total = 0.0
    for r in detail:
        for col in ("Audio Duration", "Video Duration"):
            if col in r:
                total += _duration_seconds(r.get(col))
    return total


def build_stats(
    bundle: dict[str, Rows], period: str, tenant_label: str = "Your organization"
) -> WrappedStats:
    email = bundle.get("email", [])
    teams = bundle.get("teams", [])
    cards: list[StatCard] = []

    sent, received = _sum(email, "Send"), _sum(email, "Receive")
    if sent or received:
        cards.append(
            StatCard(key="email", emoji="✉️", title="Emails sent",
                     value=_fmt(sent), subtitle=f"{_fmt(received)} received")
        )

    meetings = _sum(teams, "Meetings")
    chat = _sum(teams, "Team Chat Messages") + _sum(teams, "Private Chat Messages")
    if meetings:
        cards.append(
            StatCard(key="meetings", emoji="📅", title="Teams meetings",
                     value=_fmt(meetings), subtitle="joined across the org")
        )

    # Signature "wow": time in Teams calls & meetings → hours → years.
    secs = _meeting_seconds(bundle.get("teams_detail", []))
    hours = round(secs / 3600)
    if hours >= 1:
        if hours >= _HOURS_PER_YEAR:
            years = hours / _HOURS_PER_YEAR
            value = f"{years:.1f} years"
            sub = f"{_fmt(hours)} hours" + (f" · {_fmt(meetings)} meetings" if meetings else "")
        else:
            value = f"{_fmt(hours)} hours"
            sub = f"{_fmt(meetings)} meetings" if meetings else "in Teams calls & meetings"
        cards.append(
            StatCard(key="hours", emoji="⏱️", title="Spent in Teams calls & meetings",
                     value=value, subtitle=sub)
        )

    if chat:
        cards.append(
            StatCard(key="chat", emoji="💬", title="Chat messages",
                     value=_fmt(chat), subtitle="Teams team + private chats")
        )

    shared = sum(
        _sum(bundle.get(src, []), col)
        for src in ("onedrive_activity", "sharepoint_activity")
        for col in ("Shared Internally", "Shared Externally")
    )
    if shared:
        cards.append(
            StatCard(key="docs_shared", emoji="🤝", title="Documents shared",
                     value=_fmt(shared), subtitle="internally + externally")
        )

    au = bundle.get("active_users", [])
    apps = ["Exchange", "OneDrive", "SharePoint", "Teams", "Yammer", "Skype For Business"]
    totals = {a: _sum(au, a) for a in apps if any(a in r for r in au)}
    totals = {a: v for a, v in totals.items() if v}
    if totals:
        top = max(totals, key=lambda k: totals[k])
        cards.append(
            StatCard(key="top_app", emoji="🏆", title="Most-used app",
                     value=top, subtitle=f"{_fmt(totals[top])} active-user-days")
        )

    files = (
        _latest_max(bundle.get("onedrive_files", []), "Total")
        + _latest_max(bundle.get("sharepoint_files", []), "Total")
    )
    if files:
        cards.append(
            StatCard(key="files", emoji="📄", title="Files stored",
                     value=_fmt(files), subtitle="OneDrive + SharePoint")
        )

    storage = (
        _latest_max(bundle.get("mailbox_storage", []), "Storage Used (Byte)")
        + _latest_max(bundle.get("onedrive_storage", []), "Storage Used (Byte)")
        + _latest_max(bundle.get("sharepoint_storage", []), "Storage Used (Byte)")
    )
    if storage:
        cards.append(
            StatCard(key="storage", emoji="📁", title="Data stored",
                     value=_fmt_bytes(storage), subtitle="mailbox + OneDrive + SharePoint")
        )

    if email:
        best = max(email, key=lambda r: _to_int(r.get("Send", 0)) + _to_int(r.get("Receive", 0)))
        day = best.get("Report Date", "")
        if day:
            n = _to_int(best.get("Send", 0)) + _to_int(best.get("Receive", 0))
            try:
                day_label = datetime.strptime(day, "%Y-%m-%d").strftime("%-d %b")
            except ValueError:
                day_label = day
            cards.append(
                StatCard(key="busiest", emoji="🔥", title="Busiest day",
                         value=day_label, subtitle=f"{_fmt(n)} emails in a day")
            )

    peak_active = _latest_max(au, "Office 365") or _latest_max(au, "Office365")
    if peak_active:
        cards.append(
            StatCard(key="active", emoji="🧑‍💻", title="People active",
                     value=_fmt(peak_active), subtitle="on Microsoft 365 in a day")
        )

    # Time span + daily activity trend (so the numbers mean something over a period).
    dated = sorted((r for r in email if r.get("Report Date")), key=lambda r: r["Report Date"])
    date_start = dated[0]["Report Date"] if dated else ""
    date_end = dated[-1]["Report Date"] if dated else ""
    trend = [_to_int(r.get("Send", 0)) + _to_int(r.get("Receive", 0)) for r in dated]

    return WrappedStats(
        period=period, generated_at=datetime.now(timezone.utc),
        tenant_label=tenant_label, cards=cards,
        date_start=date_start, date_end=date_end, trend=trend, raw=bundle,
    )

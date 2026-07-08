"""Deterministic synthetic tenant — powers `m365-wrapped demo` (no Azure needed).

Numbers model a ~2,500-seat org over 180 days: big enough to show the "wow", shaped
so every card renders. Same column names the real Graph reports return, so the demo
exercises the exact aggregation path.
"""

from __future__ import annotations

import math
import random
from datetime import date, timedelta

Rows = list[dict[str, str]]

_TB = 1024**4
_SEED = 42
_USERS = 2487
_DAYS = 180


def _iso(seconds: float) -> str:
    h = int(seconds // 3600)
    m = int((seconds % 3600) // 60)
    return f"PT{h}H{m}M"


def demo_bundle() -> dict[str, Rows]:
    rng = random.Random(_SEED)
    start = date(2026, 1, 1)

    email: Rows = []
    teams: Rows = []
    active: Rows = []
    od_act: Rows = []
    sp_act: Rows = []
    for i in range(_DAYS):
        d = start + timedelta(days=i)
        weekday = d.weekday()
        workday = weekday < 5
        # weekly rhythm + a single spike day (the "busiest day" card)
        base = 1.0 if workday else 0.18
        wave = 0.85 + 0.3 * math.sin(i / 6.0)
        spike = 2.35 if i == 73 else 1.0
        f = base * wave * spike

        send = int(38_000 * f * (0.95 + rng.random() * 0.1))
        recv = int(54_000 * f * (0.95 + rng.random() * 0.1))
        email.append({"Report Date": d.isoformat(), "Send": str(send),
                      "Receive": str(recv), "Read": str(int(recv * 0.7))})

        teams.append({
            "Report Date": d.isoformat(),
            "Meetings": str(int(1_450 * f)),
            "Team Chat Messages": str(int(16_800 * f)),
            "Private Chat Messages": str(int(9_400 * f)),
        })

        act = int(_USERS * (0.96 if workday else 0.34) * (0.98 + rng.random() * 0.04))
        active.append({
            "Report Date": d.isoformat(),
            "Office 365": str(act),
            "Exchange": str(int(act * 0.94)),
            "Teams": str(int(act * 0.97)),
            "SharePoint": str(int(act * 0.71)),
            "OneDrive": str(int(act * 0.66)),
        })

        od_act.append({"Report Date": d.isoformat(),
                       "Shared Internally": str(int(2_000 * f)),
                       "Shared Externally": str(int(420 * f))})
        sp_act.append({"Report Date": d.isoformat(),
                       "Shared Internally": str(int(3_200 * f)),
                       "Shared Externally": str(int(640 * f))})

    # Per-user Teams detail → total call/meeting time (the "years in meetings" card).
    teams_detail: Rows = []
    for u in range(_USERS):
        audio_h = 150 + rng.random() * 120   # ~150–270h audio over the window
        video_h = 35 + rng.random() * 55
        teams_detail.append({
            "User Principal Name": f"user{u:04d}@contoso.com",
            "Audio Duration": _iso(audio_h * 3600),
            "Video Duration": _iso(video_h * 3600),
            "Meeting Count": str(int(60 + rng.random() * 90)),
        })

    return {
        "email": email,
        "teams": teams,
        "active_users": active,
        "teams_detail": teams_detail,
        "mailbox_storage": [{"Storage Used (Byte)": str(int(23 * _TB))}],
        "onedrive_storage": [{"Storage Used (Byte)": str(int(181 * _TB))}],
        "sharepoint_storage": [{"Storage Used (Byte)": str(int(138 * _TB))}],
        "onedrive_files": [{"Total": str(1_240_000)}],
        "sharepoint_files": [{"Total": str(3_480_000)}],
        "onedrive_activity": od_act,
        "sharepoint_activity": sp_act,
    }

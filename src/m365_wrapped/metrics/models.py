from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, Field


class StatCard(BaseModel):
    key: str
    emoji: str
    title: str
    value: str
    subtitle: str = ""


class WrappedStats(BaseModel):
    period: str
    generated_at: datetime
    tenant_label: str = "Your organization"
    cards: list[StatCard] = Field(default_factory=list)
    date_start: str = ""            # first day covered (YYYY-MM-DD), from the data
    date_end: str = ""             # last day covered
    trend: list[int] = Field(default_factory=list)  # daily activity, for the sparkline
    raw: dict = Field(default_factory=dict)

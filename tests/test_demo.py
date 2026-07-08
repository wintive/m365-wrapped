from m365_wrapped.demo import demo_bundle
from m365_wrapped.metrics.aggregate import build_stats


def test_demo_produces_full_card_set() -> None:
    stats = build_stats(demo_bundle(), "D180", tenant_label="Contoso")
    keys = {c.key for c in stats.cards}
    assert {
        "email", "meetings", "hours", "chat", "docs_shared",
        "top_app", "files", "storage", "busiest", "active",
    } <= keys


def test_demo_hours_card_is_the_wow() -> None:
    stats = build_stats(demo_bundle(), "D180")
    hours = next(c for c in stats.cards if c.key == "hours")
    assert hours.value.endswith("years")          # big org -> years, not hours
    assert "hours" in hours.subtitle


def test_demo_is_deterministic() -> None:
    a = build_stats(demo_bundle(), "D180")
    b = build_stats(demo_bundle(), "D180")
    assert [c.value for c in a.cards] == [c.value for c in b.cards]

from m365_wrapped.metrics.aggregate import _duration_seconds, build_stats


def test_duration_parsing_variants() -> None:
    assert _duration_seconds("PT1H30M") == 5400
    assert _duration_seconds("PT45M") == 2700
    assert _duration_seconds("01:00:00") == 3600
    assert _duration_seconds("3600") == 3600
    assert _duration_seconds("") == 0
    assert _duration_seconds("garbage") == 0


def test_hours_card_from_teams_detail() -> None:
    bundle = {
        "email": [{"Send": "1", "Receive": "1", "Report Date": "2026-01-01"}],
        "teams": [{"Meetings": "4"}],
        "teams_detail": [
            {"Audio Duration": "PT1H", "Video Duration": "PT30M"},
            {"Audio Duration": "PT1H", "Video Duration": "PT30M"},
        ],
    }
    stats = build_stats(bundle, "D30")
    hours = next(c for c in stats.cards if c.key == "hours")
    assert hours.value == "3 hours"  # 2*(60+30)min = 3h, below a year
    assert "4 meetings" in hours.subtitle


def test_build_stats_basic() -> None:
    bundle = {
        "email": [
            {"Send": "10", "Receive": "20", "Read": "5", "Report Date": "2026-01-01"},
            {"Send": "30", "Receive": "40", "Read": "5", "Report Date": "2026-01-02"},
        ],
        "teams": [{"Meetings": "3", "Team Chat Messages": "7", "Private Chat Messages": "2"}],
        "mailbox_storage": [{"Storage Used (Byte)": "1048576"}],
        "onedrive_storage": [],
        "sharepoint_storage": [],
        "active_users": [{"Teams": "5", "Exchange": "3"}],
    }
    stats = build_stats(bundle, "D180")
    keys = {c.key for c in stats.cards}
    assert {"email", "meetings", "storage", "top_app", "busiest"} <= keys

    email = next(c for c in stats.cards if c.key == "email")
    assert email.value == "40"  # 10 + 30

    busiest = next(c for c in stats.cards if c.key == "busiest")
    assert busiest.value == "2 Jan"  # humanized from 2026-01-02

    top_app = next(c for c in stats.cards if c.key == "top_app")
    assert top_app.value == "Teams"


def test_stats_carry_timeframe_and_trend() -> None:
    from m365_wrapped.demo import demo_bundle

    stats = build_stats(demo_bundle(), "D180")
    assert stats.date_start and stats.date_end
    assert stats.date_start < stats.date_end
    assert len(stats.trend) > 100  # a daily activity series across the window

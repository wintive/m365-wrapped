import httpx

from m365_wrapped.graph.client import GraphClient

CSV = "Report Date,Send,Receive\r\n2026-01-01,10,20\r\n2026-01-02,30,40\r\n"


def test_report_csv_parses_rows() -> None:
    def handler(request: httpx.Request) -> httpx.Response:
        assert "getEmailActivityCounts(period='D30')" in str(request.url)
        return httpx.Response(200, content=("﻿" + CSV).encode("utf-8"))

    c = GraphClient("tok", transport=httpx.MockTransport(handler))
    rows = c.report_csv("getEmailActivityCounts", "D30")
    assert len(rows) == 2
    assert rows[0]["Send"] == "10" and rows[1]["Receive"] == "40"


def test_report_csv_retries_on_429() -> None:
    calls = {"n": 0}

    def handler(request: httpx.Request) -> httpx.Response:
        calls["n"] += 1
        if calls["n"] == 1:
            return httpx.Response(429, headers={"Retry-After": "0"})
        return httpx.Response(200, content=CSV.encode("utf-8"))

    c = GraphClient("tok", transport=httpx.MockTransport(handler))
    rows = c.report_csv("getEmailActivityCounts", "D7")
    assert calls["n"] == 2 and len(rows) == 2

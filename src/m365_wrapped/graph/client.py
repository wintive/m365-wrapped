from __future__ import annotations

import csv
import io
import time

import httpx

GRAPH = "https://graph.microsoft.com/v1.0"


class GraphClient:
    """Minimal Graph client for the usage-report endpoints (return CSV)."""

    def __init__(
        self, token: str, timeout: float = 60.0, transport: httpx.BaseTransport | None = None
    ) -> None:
        self._c = httpx.Client(
            base_url=GRAPH,
            headers={"Authorization": f"Bearer {token}"},
            timeout=timeout,
            follow_redirects=True,
            transport=transport,
        )

    def close(self) -> None:
        self._c.close()

    def __enter__(self) -> "GraphClient":
        return self

    def __exit__(self, *_exc: object) -> None:
        self.close()

    def report_csv(self, func: str, period: str) -> list[dict[str, str]]:
        """Call /reports/<func>(period='Dn') and return parsed CSV rows."""
        path = f"/reports/{func}(period='{period}')"
        for _ in range(4):
            r = self._c.get(path)
            if r.status_code == 429:
                time.sleep(int(r.headers.get("Retry-After", "5")))
                continue
            r.raise_for_status()
            return list(csv.DictReader(io.StringIO(r.content.decode("utf-8-sig"))))
        raise RuntimeError(f"Throttled repeatedly on {func}")

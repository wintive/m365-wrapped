from __future__ import annotations

from .client import GraphClient

Rows = list[dict[str, str]]


def collect_all(c: GraphClient, period: str) -> dict[str, Rows]:
    """Fetch every usage report v0.1 needs, keyed by short name.

    Detail reports (teams_detail) are summed to org totals only — never stored or
    shown per user (see docs/PRIVACY.md). A failing optional report is tolerated so
    one missing endpoint never sinks the whole run.
    """
    bundle: dict[str, Rows] = {
        "email": c.report_csv("getEmailActivityCounts", period),
        "teams": c.report_csv("getTeamsUserActivityCounts", period),
        "mailbox_storage": c.report_csv("getMailboxUsageStorage", period),
        "onedrive_storage": c.report_csv("getOneDriveUsageStorage", period),
        "sharepoint_storage": c.report_csv("getSharePointSiteUsageStorage", period),
        "active_users": c.report_csv("getOffice365ActiveUserCounts", period),
    }
    # Optional reports (best-effort — one missing endpoint never sinks the run):
    #  - teams_detail: call/meeting durations for the "time in meetings" card
    #  - *_files:      file counts stored (OneDrive + SharePoint)
    #  - *_activity:   files shared internally/externally = "documents shared"
    for key, func in (
        ("teams_detail", "getTeamsUserActivityUserDetail"),
        ("onedrive_files", "getOneDriveUsageFileCounts"),
        ("sharepoint_files", "getSharePointSiteUsageFileCounts"),
        ("onedrive_activity", "getOneDriveActivityFileCounts"),
        ("sharepoint_activity", "getSharePointActivityFileCounts"),
    ):
        try:
            bundle[key] = c.report_csv(func, period)
        except Exception:
            bundle[key] = []
    return bundle

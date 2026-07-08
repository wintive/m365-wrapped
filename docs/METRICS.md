# Metrics → Graph endpoints

Every card is derived from a documented Microsoft Graph **usage report** (read-only, `Reports.Read.All`).
Reports are returned as CSV and aggregated over the selected `period` (D7/D30/D90/D180).

| Card | Stat | Graph report function | Columns used |
|---|---|---|---|
| ✉️ Emails | sent / received | `getEmailActivityCounts(period)` | `Send`, `Receive`, `Read`, `Report Date` |
| 📅 Teams | meetings + chat | `getTeamsUserActivityCounts(period)` | `Meetings`, `Team Chat Messages`, `Private Chat Messages` |
| ⏱️ Time in meetings | hours → years | `getTeamsUserActivityUserDetail(period)` | `Audio Duration` + `Video Duration` (summed to org total) |
| 🏆 Most-used app | top app | `getOffice365ActiveUserCounts(period)` | `Exchange`,`OneDrive`,`SharePoint`,`Teams`,… |
| 📁 Storage | total bytes | `getMailboxUsageStorage` + `getOneDriveUsageStorage` + `getSharePointSiteUsageStorage` | `Storage Used (Byte)` (latest) |
| 🔥 Busiest day | peak email day | `getEmailActivityCounts(period)` | `Send`+`Receive` per `Report Date` |
| 🧑‍💻 People active | peak active users | `getOffice365ActiveUserCounts(period)` | `Office 365` (daily peak) |

> **Durations** (`Audio/Video Duration`) are parsed from ISO-8601 (`PT1H30M`), `HH:MM:SS`, or raw
> seconds, then **summed across all users** into a single org total — no per-user value is stored or
> shown. `years = hours / 8760`.

### Roadmap (v0.2+)
- **Meeting *hours*** (not just counts) via the Teams user-activity *detail* report (duration fields).
- **True 12-month** recap via a monthly snapshot accumulator (works around the 180-day cap).
- More cards: SharePoint/OneDrive file counts, active-user growth, per-app breakdown.

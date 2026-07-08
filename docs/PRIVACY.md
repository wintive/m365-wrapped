# Privacy

M365 Wrapped is **org-aggregate only**. It reads Microsoft 365 **usage reports** (daily totals),
never message content, files, calendars, chats, or security configuration.

- **One Graph permission:** `Reports.Read.All` (Application, read-only).
- **No per-user tracking:** cards show organization-wide totals and superlatives; individuals are
  never singled out.
- **Detail reports are summed, not stored:** the "time in meetings" card reads a per-user usage
  report only to **sum** its duration columns into one org total. Per-user rows are never written to
  `stats.json`, the cards, or anywhere on disk.
- **Concealed names:** if your tenant enables *"Display concealed user, group, and site names"* in the
  M365 report settings, the API returns pseudonymized ids — Wrapped works the same either way.
- **Nothing leaves your machine:** all output (`cards/`, `index.html`, `stats.json`) is written
  locally. No telemetry, no phone-home.
- **Secrets:** the app takes credentials from the environment. Never commit them — use a `.env` you
  keep private, or better, inject them from your secret manager at runtime.

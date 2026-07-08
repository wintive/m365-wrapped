from __future__ import annotations

import sys
from pathlib import Path

import msal

from .config import Settings

_SCOPE_APP = ["https://graph.microsoft.com/.default"]
_SCOPE_DELEGATED = ["https://graph.microsoft.com/Reports.Read.All"]

# Wintive's multi-tenant PUBLIC client app. Lets anyone sign in with a device code —
# no app registration, no secret. A client id is not a secret (it ships in the tool,
# like the Azure CLI's own client id). Override with CLIENT_ID for your own app.
DEFAULT_CLIENT_ID = "285bd6db-d75e-4695-a78f-8adc85aaef21"


def _app_only_credential(settings: Settings):
    """Certificate (preferred) or client secret — for headless / app-only runs."""
    if settings.client_cert_path and settings.client_cert_thumbprint:
        return {
            "private_key": Path(settings.client_cert_path).read_text(),
            "thumbprint": settings.client_cert_thumbprint,
        }
    if settings.client_secret:
        return settings.client_secret
    return None


def _token(result: dict) -> str:
    tok = result.get("access_token")
    if not tok:
        raise RuntimeError(f"Auth failed: {result.get('error_description', result)}")
    return tok


def get_token(settings: Settings) -> str:
    """Graph token. App-only if a secret/cert is set; otherwise interactive device-code."""
    cred = _app_only_credential(settings)
    if cred is not None:
        # Headless app-only (client credentials): needs tenant + client + secret/cert.
        if not (settings.tenant_id and settings.client_id):
            raise RuntimeError("App-only auth needs TENANT_ID + CLIENT_ID — see docs/SETUP.md")
        app = msal.ConfidentialClientApplication(
            client_id=settings.client_id,
            authority=f"https://login.microsoftonline.com/{settings.tenant_id}",
            client_credential=cred,
        )
        return _token(app.acquire_token_for_client(scopes=_SCOPE_APP))

    # Delegated device-code (default): just sign in — no app registration needed.
    client_id = settings.client_id or DEFAULT_CLIENT_ID
    authority = f"https://login.microsoftonline.com/{settings.tenant_id or 'organizations'}"
    app = msal.PublicClientApplication(client_id=client_id, authority=authority)

    accounts = app.get_accounts()
    if accounts:
        silent = app.acquire_token_silent(_SCOPE_DELEGATED, account=accounts[0])
        if silent:
            return _token(silent)

    flow = app.initiate_device_flow(scopes=_SCOPE_DELEGATED)
    if "user_code" not in flow:
        raise RuntimeError(f"Could not start device sign-in: {flow.get('error_description', flow)}")
    print(flow["message"], file=sys.stderr, flush=True)
    return _token(app.acquire_token_by_device_flow(flow))

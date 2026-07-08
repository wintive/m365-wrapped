import pytest

from m365_wrapped import auth
from m365_wrapped.config import Settings


class _FakeConfidential:
    last_credential = None

    def __init__(self, client_id, authority, client_credential):
        _FakeConfidential.last_credential = client_credential

    def acquire_token_for_client(self, scopes):
        return {"access_token": "app-tok"}


class _FakePublic:
    last_client_id = None

    def __init__(self, client_id, authority):
        _FakePublic.last_client_id = client_id

    def get_accounts(self):
        return []

    def initiate_device_flow(self, scopes):
        return {"user_code": "ABCD", "message": "go to microsoft.com/devicelogin"}

    def acquire_token_by_device_flow(self, flow):
        return {"access_token": "device-tok"}


@pytest.fixture
def fake_msal(monkeypatch):
    monkeypatch.setattr(auth.msal, "ConfidentialClientApplication", _FakeConfidential)
    monkeypatch.setattr(auth.msal, "PublicClientApplication", _FakePublic)
    _FakeConfidential.last_credential = None
    _FakePublic.last_client_id = None


def test_secret_uses_app_only(fake_msal) -> None:
    s = Settings(tenant_id="t", client_id="c", client_secret="sesame")
    assert auth.get_token(s) == "app-tok"
    assert _FakeConfidential.last_credential == "sesame"


def test_certificate_preferred_over_secret(fake_msal, tmp_path) -> None:
    key = tmp_path / "k.pem"
    key.write_text("PEM")
    s = Settings(tenant_id="t", client_id="c", client_secret="sesame",
                 client_cert_path=str(key), client_cert_thumbprint="ABCD")
    auth.get_token(s)
    assert _FakeConfidential.last_credential == {"private_key": "PEM", "thumbprint": "ABCD"}


def test_app_only_missing_ids_raises(fake_msal) -> None:
    with pytest.raises(RuntimeError, match="TENANT_ID"):
        auth.get_token(Settings(client_secret="x"))  # credential but no tenant/client


def test_no_credential_uses_device_code(fake_msal) -> None:
    assert auth.get_token(Settings()) == "device-tok"


def test_device_code_defaults_to_shipped_client_id(fake_msal) -> None:
    auth.get_token(Settings())
    assert _FakePublic.last_client_id == auth.DEFAULT_CLIENT_ID


def test_app_only_auth_failure_raises(monkeypatch) -> None:
    class _NoTok(_FakeConfidential):
        def acquire_token_for_client(self, scopes):
            return {"error_description": "bad creds"}

    monkeypatch.setattr(auth.msal, "ConfidentialClientApplication", _NoTok)
    with pytest.raises(RuntimeError, match="Auth failed"):
        auth.get_token(Settings(tenant_id="t", client_id="c", client_secret="x"))

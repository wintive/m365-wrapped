from __future__ import annotations

from pathlib import Path

import yaml
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """Runtime config. Values come from environment variables (or a local .env file)."""

    model_config = SettingsConfigDict(
        env_file=".env", env_file_encoding="utf-8", case_sensitive=False, extra="ignore"
    )

    tenant_id: str = ""
    client_id: str = ""
    # App-only credential — either a client secret (easy) OR a certificate (preferred):
    client_secret: str = ""
    client_cert_path: str = ""        # PEM private key path
    client_cert_thumbprint: str = ""  # SHA-1 thumbprint (hex, no colons)

    period: str = "D180"
    anonymize: bool = False
    brand_logo: str | None = None
    out_dir: str = "./out"


def load_settings(config_path: str | None = "config.yaml") -> Settings:
    overrides: dict = {}
    if config_path:
        p = Path(config_path)
        if p.exists():
            overrides = yaml.safe_load(p.read_text()) or {}
    return Settings(**{k: v for k, v in overrides.items() if v is not None})

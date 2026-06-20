"""Application configuration.

Loads settings from environment variables. If Vault integration is enabled
(VAULT_ADDR + VAULT_TOKEN present), DB credentials are pulled from Vault and
override the plain environment values. This keeps secrets out of the image
and out of plain env in production while still working locally with SQLite.
"""
import logging
import os
from functools import lru_cache

logger = logging.getLogger("grocery.config")


class Settings:
    def __init__(self) -> None:
        self.app_name: str = os.getenv("APP_NAME", "Grocery Delivery Platform")
        self.environment: str = os.getenv("ENVIRONMENT", "dev")

        # Default to a local SQLite file so the app runs with zero infra.
        self.database_url: str = os.getenv(
            "DATABASE_URL", "sqlite:///./grocery.db"
        )

        # Optional Vault integration (see app/vault_client.py).
        self.vault_addr: str = os.getenv("VAULT_ADDR", "")
        self.vault_token: str = os.getenv("VAULT_TOKEN", "")
        self.vault_secret_path: str = os.getenv(
            "VAULT_SECRET_PATH", "secret/data/grocery"
        )

        self._apply_vault_overrides()

    def _apply_vault_overrides(self) -> None:
        if not (self.vault_addr and self.vault_token):
            return
        try:
            from app.vault_client import read_secret

            data = read_secret(
                self.vault_addr, self.vault_token, self.vault_secret_path
            )
            if data.get("database_url"):
                self.database_url = data["database_url"]
                logger.info("Loaded database_url from Vault")
        except Exception as exc:  # pragma: no cover - best-effort
            logger.warning("Vault override failed, using env values: %s", exc)


@lru_cache
def get_settings() -> Settings:
    return Settings()

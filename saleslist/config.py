from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

from .errors import AuthenticationError


@dataclass(frozen=True)
class Settings:
    request_interval_seconds: float = 1.0
    max_retries: int = 2
    retry_delay_seconds: float = 5.0

    @classmethod
    def load(cls, env_file: Path = Path(".env")) -> "Settings":
        load_dotenv(env_file)
        return cls(
            request_interval_seconds=float(os.getenv("SALES_LIST_REQUEST_INTERVAL_SECONDS", "1.0")),
            max_retries=int(os.getenv("SALES_LIST_MAX_RETRIES", "2")),
            retry_delay_seconds=float(os.getenv("SALES_LIST_RETRY_DELAY_SECONDS", "5.0")),
        )


def required_credentials(platform: str) -> dict[str, str]:
    keys = {
        "instagram": ("INSTAGRAM_USERNAME", "INSTAGRAM_PASSWORD"),
        "x": ("X_USERNAME", "X_EMAIL", "X_PASSWORD"),
    }[platform]
    values = {key: os.getenv(key, "") for key in keys}
    missing = [key for key, value in values.items() if not value]
    if missing:
        raise AuthenticationError(f"Missing required values in .env: {', '.join(missing)}")
    return values

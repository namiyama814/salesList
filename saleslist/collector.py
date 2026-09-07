from __future__ import annotations

import time

from .clients import FollowerClient
from .config import Settings
from .csv_io import CsvWriter
from .errors import NetworkError


def collect_target(
    client: FollowerClient, target: str, writer: CsvWriter, settings: Settings, *,
    limit: int | None, already_seen: set[str] | None = None,
) -> int:
    seen = already_seen if already_seen is not None else set()
    written = 0
    attempts = 0
    while True:
        try:
            for follower in client.followers(target):
                key = follower.username.casefold()
                if key in seen:
                    continue
                writer.write(follower)
                seen.add(key)
                written += 1
                if limit is not None and written >= limit:
                    return written
            return written
        except NetworkError:
            if attempts >= settings.max_retries:
                raise
            attempts += 1
            time.sleep(settings.retry_delay_seconds)
    return written

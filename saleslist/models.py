from __future__ import annotations

from dataclasses import asdict, dataclass
from datetime import datetime
from typing import Literal


DMStatus = Literal["available", "unavailable", "unknown"]

CSV_COLUMNS = (
    "platform",
    "username",
    "display_name",
    "profile_url",
    "bio",
    "followers_count",
    "following_count",
    "is_private",
    "dm_status",
    "collected_at",
)


@dataclass(frozen=True)
class Follower:
    platform: str
    username: str
    display_name: str = ""
    profile_url: str = ""
    bio: str = ""
    followers_count: int | str = ""
    following_count: int | str = ""
    is_private: bool | str = ""
    dm_status: DMStatus = "unknown"
    collected_at: str = ""

    def csv_row(self) -> dict[str, object]:
        row = asdict(self)
        if not row["collected_at"]:
            row["collected_at"] = datetime.now().astimezone().isoformat(timespec="seconds")
        return row

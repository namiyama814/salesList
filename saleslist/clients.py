from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Iterable

from .models import Follower


class FollowerClient(ABC):
    @abstractmethod
    def followers(self, target: str) -> Iterable[Follower]: ...


def client_for(platform: str, session_dir: Path, request_interval_seconds: float = 1.0) -> FollowerClient:
    if platform == "instagram":
        from .instagram import InstagramClient
        return InstagramClient(session_dir, request_interval_seconds)
    from .x import XClient
    return XClient(session_dir, request_interval_seconds)

from __future__ import annotations

import time
import os
from pathlib import Path
from typing import Any, Iterable

from ..clients import FollowerClient
from ..config import required_credentials
from ..errors import AuthenticationError, NetworkError, PrivateTargetError, RateLimitError, TargetNotFoundError
from ..models import Follower
from ..normalizers import dm_status, value


class InstagramClient(FollowerClient):
    def __init__(self, session_dir: Path, request_interval_seconds: float = 1.0):
        self.session_path = session_dir / "instagram.json"
        self.request_interval_seconds = request_interval_seconds

    def _login(self) -> Any:
        try:
            from instagrapi import Client
        except ImportError as exc:
            raise AuthenticationError("instagrapi is not installed. Run: pip install -e .") from exc
        client = Client()
        try:
            if self.session_path.exists():
                client.load_settings(self.session_path)
            session_id = os.getenv("INSTAGRAM_SESSION_ID", "").strip()
            if session_id:
                client.login_by_sessionid(session_id)
            else:
                credentials = required_credentials("instagram")
                client.login(credentials["INSTAGRAM_USERNAME"], credentials["INSTAGRAM_PASSWORD"])
            self.session_path.parent.mkdir(parents=True, exist_ok=True)
            client.dump_settings(self.session_path)
            return client
        except Exception as exc:
            message = str(exc).lower()
            if "rate limit" in message or "429" in message or "please wait" in message:
                raise RateLimitError(f"Instagram rate limit reached: {exc}") from exc
            raise AuthenticationError(f"Instagram login failed: {exc}") from exc

    def followers(self, target: str) -> Iterable[Follower]:
        client = self._login()
        try:
            target_id = client.user_id_from_username(target)
            cursor = ""
        except Exception as exc:
            self._raise_retrieval_error(target, exc)
        try:
            while True:
                users, next_cursor = client.user_followers_v1_chunk(target_id, max_amount=200, max_id=cursor)
                for user in users:
                    status = dm_status(user)
                    if status == "unavailable":
                        continue
                    username = str(value(user, "username"))
                    yield Follower(
                        platform="instagram", username=username,
                        display_name=str(value(user, "full_name", "display_name")),
                        profile_url=f"https://www.instagram.com/{username}/",
                        bio=str(value(user, "biography", "bio")),
                        followers_count=value(user, "follower_count", "followers_count"),
                        following_count=value(user, "following_count", "friends_count"),
                        is_private=value(user, "is_private"), dm_status=status,
                    )
                if not next_cursor:
                    return
                cursor = next_cursor
                if self.request_interval_seconds > 0:
                    time.sleep(self.request_interval_seconds)
        except Exception as exc:
            self._raise_retrieval_error(target, exc)

    @staticmethod
    def _raise_retrieval_error(target: str, exc: Exception) -> None:
        message = str(exc).lower()
        if "rate limit" in message or "429" in message or "please wait" in message:
            raise RateLimitError(f"Instagram rate limit reached: {exc}") from exc
        if "private" in message:
            raise PrivateTargetError(f"Instagram target is private or inaccessible: {target}") from exc
        if "not found" in message or "does not exist" in message:
            raise TargetNotFoundError(f"Instagram target not found: {target}") from exc
        raise NetworkError(f"Instagram follower retrieval failed: {exc}") from exc

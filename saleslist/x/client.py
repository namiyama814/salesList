from __future__ import annotations

import json
import time
from pathlib import Path
from typing import Any, Iterable

from ..clients import FollowerClient
from ..errors import AuthenticationError, NetworkError, PrivateTargetError, RateLimitError, TargetNotFoundError
from ..models import Follower
from ..normalizers import dm_status, value


class XClient(FollowerClient):
    """Read X followers with tweetkit-x and a logged-in browser cookie."""

    def __init__(self, session_dir: Path, request_interval_seconds: float = 1.0):
        self.request_interval_seconds = request_interval_seconds

    def _users(self, target: str) -> Iterable[dict[str, Any]]:
        try:
            from tweetkit_x import TweetKit
            from tweetkit_x.client import C, _walk_users
            client = TweetKit()
            target_id = client.user_id_by_name(target)
            cursor: str | None = None
            while True:
                operation = "Followers"
                query_id = C.QUERY_IDS[operation]
                variables: dict[str, Any] = {"userId": target_id, "count": 20, "includePromotedContent": False}
                if cursor:
                    variables["cursor"] = cursor
                path = f"/i/api/graphql/{query_id}/{operation}"
                response = client._session.get(
                    f"{C.GQL_BASE}/{query_id}/{operation}",
                    params={"variables": json.dumps(variables), "features": json.dumps(C.USER_TWEETS_FEATURES)},
                    headers=client._headers("GET", path), timeout=client.timeout,
                )
                if response.status_code != 200:
                    raise RuntimeError(f"Followers HTTP {response.status_code}: {response.text[:200]}")
                page: dict[str, dict[str, Any]] = {}
                next_cursor = _walk_users(response.json(), page)
                if not page:
                    return
                yield from page.values()
                if not next_cursor or next_cursor == cursor:
                    return
                cursor = next_cursor
                if self.request_interval_seconds > 0:
                    time.sleep(self.request_interval_seconds)
        except Exception as exc:
            message = str(exc).lower()
            if "cookie" in message or "401" in message or "403" in message or "unauthorized" in message:
                raise AuthenticationError(f"X browser session is invalid: {exc}") from exc
            if "could not resolve" in message or "not found" in message:
                raise TargetNotFoundError(f"X target not found: {target}") from exc
            if "protected" in message or "private" in message:
                raise PrivateTargetError(f"X target is protected or inaccessible: {target}") from exc
            if "429" in message or "rate limit" in message:
                raise RateLimitError(f"X rate limit reached: {exc}") from exc
            raise NetworkError(f"X follower retrieval failed: {exc}") from exc

    def followers(self, target: str) -> Iterable[Follower]:
        for user in self._users(target):
            status = dm_status(user)
            if status == "unavailable":
                continue
            username = str(value(user, "username", "screen_name"))
            yield Follower(
                platform="x", username=username, display_name=str(value(user, "name", "display_name")),
                profile_url=f"https://x.com/{username}", bio=str(value(user, "bio", "description")),
                followers_count=value(user, "followers", "followers_count"), following_count=value(user, "following", "friends_count"),
                is_private=value(user, "protected", "is_private"), dm_status=status,
            )

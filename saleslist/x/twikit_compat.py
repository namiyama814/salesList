"""Small compatibility fixes for the currently released Twikit.

Twikit 2.3.3 expects an older x.com homepage representation for the
``ondemand.s`` JavaScript chunk used to produce request transaction IDs.  It
also assumes every optional field in a user payload is present.  Both are
read-only compatibility fixes; they do not alter rate limits or automate any
write action.

Remove this module when a Twikit release incorporates equivalent fixes.
"""
from __future__ import annotations

import re
from typing import Any


_applied = False


def apply() -> None:
    """Apply the Twikit 2.3.3 compatibility patches exactly once."""
    global _applied
    if _applied:
        return

    try:
        transaction = __import__(
            "twikit.x_client_transaction.transaction", fromlist=["ClientTransaction"]
        )
        user_module = __import__("twikit.user", fromlist=["User"])
    except ImportError:
        # The caller turns a missing Twikit installation into a user-facing error.
        return

    chunk_index_pattern = re.compile(r",(\d+):[\"']ondemand\.s[\"']")
    chunk_hash_template = r',{}:[\"\']([0-9a-f]+)[\"\']'

    async def get_indices(self: Any, home_page_response: Any, session: Any, headers: Any) -> tuple[int, list[int]]:
        response = self.validate_response(home_page_response) or self.home_page_response
        chunk_index_match = chunk_index_pattern.search(str(response))
        if not chunk_index_match:
            raise Exception("Couldn't get KEY_BYTE indices (ondemand.s index not found)")
        hash_match = re.compile(chunk_hash_template.format(chunk_index_match.group(1))).search(str(response))
        if not hash_match:
            raise Exception("Couldn't get KEY_BYTE indices (ondemand.s hash not found)")

        url = "https://abs.twimg.com/responsive-web/client-web/ondemand.s.{}a.js".format(hash_match.group(1))
        javascript = await session.request(method="GET", url=url, headers=headers)
        indices = [int(match.group(2)) for match in transaction.INDICES_REGEX.finditer(str(javascript.text))]
        if not indices:
            raise Exception("Couldn't get KEY_BYTE indices")
        return indices[0], indices[1:]

    original_user_init = user_module.User.__init__

    class LenientDict(dict):
        def __missing__(self, key: object) -> "LenientDict":
            return LenientDict()

    def lenient(value: Any) -> Any:
        if isinstance(value, dict):
            return LenientDict((key, lenient(item)) for key, item in value.items())
        if isinstance(value, list):
            return [lenient(item) for item in value]
        return value

    def user_init(self: Any, client: Any, data: Any) -> None:
        original_user_init(self, client, lenient(data) if isinstance(data, dict) else data)

    transaction.ClientTransaction.get_indices = get_indices
    user_module.User.__init__ = user_init
    _applied = True

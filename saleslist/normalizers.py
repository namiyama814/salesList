from __future__ import annotations

from typing import Any


def value(source: Any, *names: str, default: Any = "") -> Any:
    for name in names:
        if isinstance(source, dict) and name in source:
            return source[name]
        if hasattr(source, name):
            return getattr(source, name)
    return default


def dm_status(source: Any) -> str:
    """Use only a platform-provided capability flag; never open/send a DM."""
    for name in ("can_dm", "can_message", "dm_enabled"):
        candidate = value(source, name, default=None)
        if candidate is True:
            return "available"
        if candidate is False:
            return "unavailable"
    return "unknown"

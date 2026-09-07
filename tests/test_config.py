import pytest

from saleslist.config import required_credentials
from saleslist.errors import AuthenticationError


def test_missing_credentials_are_actionable(monkeypatch):
    monkeypatch.delenv("INSTAGRAM_USERNAME", raising=False)
    monkeypatch.delenv("INSTAGRAM_PASSWORD", raising=False)
    with pytest.raises(AuthenticationError, match="INSTAGRAM_USERNAME"):
        required_credentials("instagram")

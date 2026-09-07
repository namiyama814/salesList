class SalesListError(Exception):
    """Base exception for user-actionable collection failures."""


class AuthenticationError(SalesListError):
    """Credentials are missing or rejected."""


class TargetNotFoundError(SalesListError):
    """The requested source account could not be found."""


class PrivateTargetError(SalesListError):
    """The source account cannot be read with the current login."""


class RateLimitError(SalesListError):
    """The platform asked the collector to slow down or stop."""


class NetworkError(SalesListError):
    """A transient network or platform failure occurred."""

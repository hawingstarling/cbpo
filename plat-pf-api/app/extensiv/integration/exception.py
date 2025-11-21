class ExtensivAPIError(Exception):
    """Base exception for Extensiv API issues."""
    pass

class ExtensivRateLimitError(ExtensivAPIError):
    """Raised on 429 errors when max retries are exceeded."""
    pass
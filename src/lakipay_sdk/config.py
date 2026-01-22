from __future__ import annotations

from dataclasses import dataclass
from typing import Literal, Optional

Environment = Literal["sandbox", "production", "custom"]


def resolve_base_url(environment: Environment, override: Optional[str] = None) -> str:
    """Resolve the API base URL from environment or explicit override."""
    if override:
        return override.rstrip("/")
    if environment == "sandbox":
        # If you ever expose a sandbox host, change here
        return "https://api.lakipay.co"
    if environment == "production":
        return "https://api.lakipay.co"
    # custom without override just falls back to production host
    return "https://api.lakipay.co"


@dataclass
class LakipayConfig:
    api_key: str
    environment: Environment = "sandbox"
    base_url: Optional[str] = None
    timeout_seconds: float = 30.0
    retries: int = 2
    backoff_ms: int = 300
    log_requests: bool = False

    def resolved_base_url(self) -> str:
        return resolve_base_url(self.environment, self.base_url)


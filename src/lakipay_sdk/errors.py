from __future__ import annotations

from typing import Any, Dict, Optional


class LakipayError(Exception):
    """Represents an error returned by the Lakipay API or SDK."""

    def __init__(
        self,
        message: str,
        *,
        status: Optional[int] = None,
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
    ) -> None:
        super().__init__(message)
        self.message = message
        self.status = status
        self.code = code
        self.details = details or {}

    def __str__(self) -> str:  # pragma: no cover - trivial
        base = self.message
        meta = []
        if self.status is not None:
            meta.append(f"status={self.status}")
        if self.code:
            meta.append(f"code={self.code}")
        if meta:
            return f"{base} ({', '.join(meta)})"
        return base


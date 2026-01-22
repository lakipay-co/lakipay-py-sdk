from __future__ import annotations

import time
from typing import Any, Dict, Optional, TypeVar

import requests

from .config import LakipayConfig
from .errors import LakipayError

T = TypeVar("T")


class HttpClient:
    """Simple HTTP client wrapper with retries and basic logging."""

    def __init__(self, config: LakipayConfig) -> None:
        self._cfg = config
        self._session = requests.Session()

    def request(
        self,
        method: str,
        url: str,
        *,
        headers: Optional[Dict[str, str]] = None,
        json_body: Optional[Dict[str, Any]] = None,
        timeout: Optional[float] = None,
    ) -> Dict[str, Any]:
        timeout = timeout or self._cfg.timeout_seconds
        headers = headers or {}

        attempt = 0
        last_exc: Optional[Exception] = None

        while attempt <= self._cfg.retries:
            try:
                if self._cfg.log_requests:
                    print(f"[LakipaySDK] {method} {url} body={json_body}")

                resp = self._session.request(
                    method=method,
                    url=url,
                    headers=headers,
                    json=json_body,
                    timeout=timeout,
                )

                if self._cfg.log_requests:
                    print(
                        f"[LakipaySDK] <- {resp.status_code} "
                        f"body={resp.text[:500]}"
                    )

                # Raise for non-2xx HTTP; the API itself may still return 200 with
                # logical errors, which we handle in payments layer.
                if not resp.ok:
                    raise LakipayError(
                        f"HTTP error from Lakipay API: {resp.status_code}",
                        status=resp.status_code,
                    )

                try:
                    return resp.json()
                except ValueError as exc:
                    raise LakipayError(
                        "Failed to parse JSON response from Lakipay API",
                        status=resp.status_code,
                    ) from exc

            except (requests.RequestException, LakipayError) as exc:
                last_exc = exc
                if attempt >= self._cfg.retries:
                    break
                backoff_sec = (self._cfg.backoff_ms / 1000.0) * (2 ** attempt)
                time.sleep(backoff_sec)
                attempt += 1

        if isinstance(last_exc, LakipayError):
            raise last_exc
        raise LakipayError("Request to Lakipay API failed") from last_exc


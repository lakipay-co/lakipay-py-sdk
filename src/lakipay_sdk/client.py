from __future__ import annotations

from .config import LakipayConfig, Environment
from .http import HttpClient
from .payments import PaymentsClient
from .webhooks import WebhookClient


class LakipaySDK:
    """
    High-level entry point for the Lakipay Python SDK.

    Example:
        from lakipay_sdk import LakipaySDK

        sdk = LakipaySDK(
            api_key="pk_test_xxx:sk_test_xxx",
            environment="sandbox",
            log_requests=True,
        )

        res = sdk.payments.create_direct_payment(...)
    """

    def __init__(
        self,
        *,
        api_key: str,
        environment: Environment = "sandbox",
        base_url: str | None = None,
        timeout_seconds: float = 30.0,
        retries: int = 2,
        backoff_ms: int = 300,
        log_requests: bool = False,
    ) -> None:
        cfg = LakipayConfig(
            api_key=api_key,
            environment=environment,
            base_url=base_url,
            timeout_seconds=timeout_seconds,
            retries=retries,
            backoff_ms=backoff_ms,
            log_requests=log_requests,
        )
        http = HttpClient(cfg)

        self._config = cfg
        self._http = http

        # Public sub-clients
        self.payments = PaymentsClient(cfg, http)
        self.webhooks = WebhookClient()

    @property
    def config(self) -> LakipayConfig:
        return self._config


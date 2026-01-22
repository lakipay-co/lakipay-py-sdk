from __future__ import annotations

from typing import Any, Dict, Optional

from .config import LakipayConfig
from .errors import LakipayError
from .http import HttpClient


class PaymentsClient:
    """Payment-related API operations."""

    def __init__(self, config: LakipayConfig, http_client: HttpClient) -> None:
        self._cfg = config
        self._http = http_client

    # ----- helpers -----------------------------------------------------

    def _auth_headers(self) -> Dict[str, str]:
        return {
            "X-API-Key": self._cfg.api_key,
            "Content-Type": "application/json",
        }

    @staticmethod
    def _unwrap_response(body: Dict[str, Any]) -> Any:
        """
        Unwrap API envelope:

        {
          "status": "SUCCESS" | "ERROR",
          "message": "...",
          "data": {...},
          "error_code": "...",
          "errors": {...}
        }
        """
        status = body.get("status")
        message = body.get("message", "")

        if status == "ERROR":
            raise LakipayError(
                message or "Lakipay API returned logical error",
                status=200,
                code=body.get("error_code"),
                details=body.get("errors") or {},
            )

        return body.get("data")

    # ----- public methods ----------------------------------------------

    def create_direct_payment(
        self,
        *,
        amount: float,
        currency: str,
        phone_number: str,
        medium: str,
        reference: str,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
        redirects: Optional[Dict[str, Optional[str]]] = None,
        merchant_pays_fee: Optional[bool] = None,
    ) -> Any:
        url = f"{self._cfg.resolved_base_url()}/api/v2/payment/direct"
        body: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "phone_number": phone_number,
            "medium": medium,
            "reference": reference,
        }
        if description is not None:
            body["description"] = description
        if callback_url is not None:
            body["callback_url"] = callback_url
        if redirects is not None:
            # API expects snake_case keys if used
            snake_redirects: Dict[str, Optional[str]] = {}
            if "success" in redirects:
                snake_redirects["success_url"] = redirects.get("success")
            if "failed" in redirects:
                snake_redirects["failure_url"] = redirects.get("failed")
            body["redirects"] = snake_redirects
        if merchant_pays_fee is not None:
            body["merchant_pays_fee"] = merchant_pays_fee

        raw = self._http.request(
            "POST",
            url,
            headers=self._auth_headers(),
            json_body=body,
        )
        return self._unwrap_response(raw)

    def create_withdrawal(
        self,
        *,
        amount: float,
        currency: str,
        phone_number: str,
        medium: str,
        reference: str,
        callback_url: Optional[str] = None,
    ) -> Any:
        url = f"{self._cfg.resolved_base_url()}/api/v2/payment/withdrawal"
        body: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "phone_number": phone_number,
            "medium": medium,
            "reference": reference,
        }
        if callback_url is not None:
            body["callback_url"] = callback_url

        raw = self._http.request(
            "POST",
            url,
            headers=self._auth_headers(),
            json_body=body,
        )
        return self._unwrap_response(raw)

    def create_hosted_checkout(
        self,
        *,
        amount: float,
        currency: str,
        phone_number: str,
        reference: str,
        redirects: Dict[str, str],
        supported_mediums: Optional[list[str]] = None,
        description: Optional[str] = None,
        callback_url: Optional[str] = None,
    ) -> Any:
        url = f"{self._cfg.resolved_base_url()}/api/v2/payment/checkout"
        body: Dict[str, Any] = {
            "amount": amount,
            "currency": currency,
            "phone_number": phone_number,
            "reference": reference,
            "redirects": {
                "success_url": redirects.get("success"),
                "failure_url": redirects.get("failed"),
            },
        }
        if supported_mediums is not None:
            body["supported_mediums"] = supported_mediums
        if description is not None:
            body["description"] = description
        if callback_url is not None:
            body["callback_url"] = callback_url

        raw = self._http.request(
            "POST",
            url,
            headers=self._auth_headers(),
            json_body=body,
        )
        return self._unwrap_response(raw)

    def get_transaction(self, transaction_id: str) -> Any:
        url = (
            f"{self._cfg.resolved_base_url()}"
            f"/api/v2/payment/transaction/{transaction_id}"
        )
        raw = self._http.request(
            "GET",
            url,
            headers=self._auth_headers(),
        )
        return self._unwrap_response(raw)


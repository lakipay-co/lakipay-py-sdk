from __future__ import annotations

import base64
from dataclasses import dataclass
from typing import Any, Dict

from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.hazmat.primitives.serialization import load_pem_public_key


@dataclass
class LakipayWebhookPayload:
    event: str
    transaction_id: str
    reference: str
    amount: float
    currency: str
    status: str
    medium: str
    timestamp: str
    signature: str
    extra: Dict[str, Any]


def _build_canonical_string(payload: Dict[str, Any]) -> str:
    """
    Build canonical string by:
    - sorting keys alphabetically
    - excluding 'signature'
    - joining as key=value with '&'
    """
    parts = []
    for key in sorted(k for k in payload.keys() if k != "signature"):
        parts.append(f"{key}={payload[key]}")
    return "&".join(parts)


class WebhookClient:
    """Utilities for verifying and parsing Lakipay webhooks."""

    @staticmethod
    def verify_signature(payload: Dict[str, Any], public_key_pem: str) -> bool:
        try:
            signature_b64 = payload.get("signature", "")
            if not signature_b64:
                return False

            canonical = _build_canonical_string(payload)
            signature = base64.b64decode(signature_b64)

            public_key = load_pem_public_key(public_key_pem.encode("utf-8"))
            public_key.verify(
                signature,
                canonical.encode("utf-8"),
                padding.PKCS1v15(),
                hashes.SHA256(),
            )
            return True
        except Exception:
            return False

    @staticmethod
    def parse(raw_body: str) -> Dict[str, Any]:
        import json

        return json.loads(raw_body)

    def verify_and_parse(
        self,
        raw_body: str,
        public_key_pem: str,
    ) -> Dict[str, Any]:
        data = self.parse(raw_body)
        if not self.verify_signature(data, public_key_pem):
            raise ValueError("Invalid Lakipay webhook signature")
        return data


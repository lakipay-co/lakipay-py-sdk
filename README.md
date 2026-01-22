## Lakipay Python SDK

Python SDK for integrating with the **Lakipay core payment API** from your backend and services.

**Package:** [PyPI](https://pypi.org/project/lakipay-py-sdk/) | [GitHub](https://github.com/lakipay-co/lakipay-py-sdk)

**Requirements:**
- Python >= 3.9

---

### 1. Installation

#### Install from PyPI (Recommended)

```bash
pip install lakipay-py-sdk
# or
pip3 install lakipay-py-sdk
```

#### Install from GitHub

If you prefer to install directly from the GitHub repository:

```bash
pip install git+https://github.com/lakipay-co/lakipay-py-sdk.git
# or for a specific branch/tag
pip install git+https://github.com/lakipay-co/lakipay-py-sdk.git@main
```

### 2. Initialization

```python
from lakipay_sdk import LakipaySDK

sdk = LakipaySDK(
    api_key="pk_xxx:sk_xxx",          # X-API-Key = PUBLICKEY:SECRETKEY
    environment="production",        
    # base_url="https://api.lakipay.co",  
    timeout_seconds=30.0,
    retries=2,
    backoff_ms=300,
    log_requests=True,
)
```

---

### 3. Usage

#### 3.1 Direct Payment

```python
from lakipay_sdk import LakipaySDK, LakipayError

sdk = LakipaySDK(
    api_key="pk_xxx:sk_xxx",
    environment="production",
    log_requests=True,
)

try:
    res = sdk.payments.create_direct_payment(
        amount=20.0,
        currency="ETB",
        phone_number="2519XXXXXXXX",
        medium="TELEBIRR",
        reference="PYTEST-123",
        description="Python SDK test payment",
        callback_url="https://example.com/webhook",
        redirects={
            "success": "https://example.com/success",
            "failed": "https://example.com/failed",
        },
    )
    print(res)
except LakipayError as e:
    print("LakipayError:", e)
```

#### 3.2 Withdrawal

```python
res = sdk.payments.create_withdrawal(
    amount=1.0,
    currency="ETB",
    phone_number="2519XXXXXXXX",
    medium="CBE",
    reference="PYWD-12345",
    callback_url="https://example.com/webhook",
)
```

#### 3.3 Hosted Checkout

```python
res = sdk.payments.create_hosted_checkout(
    amount=100.0,
    currency="ETB",
    phone_number="2519XXXXXXXX",
    reference="PYHOST-12345",
    redirects={
        "success": "https://example.com/success",
        "failed": "https://example.com/failed",
    },
    supported_mediums=["MPESA", "TELEBIRR", "CBE"],
    description="Hosted checkout from Python SDK",
    callback_url="https://example.com/webhook",
)
```

#### 3.4 Get Transaction Details

```python
transaction_id = "YOUR_TRANSACTION_ID"
res = sdk.payments.get_transaction(transaction_id)
print(res)
```

Under the hood, all payment methods call:

- `POST /api/v2/payment/direct`
- `POST /api/v2/payment/withdrawal`
- `POST /api/v2/payment/checkout`
- `GET  /api/v2/payment/transaction/{id}`

---

### 4. Webhooks

Webhooks allow you to receive real‑time notifications about transaction status. Pass a `callback_url` in your requests; LakiPay will POST a signed payload there.

```python
from lakipay_sdk import LakipaySDK

sdk = LakipaySDK(api_key="dummy", environment="production")

raw_body = request.data.decode("utf-8")  # e.g. from Flask/FastAPI
public_key_pem = "-----BEGIN PUBLIC KEY-----\n...\n-----END PUBLIC KEY-----"

payload = sdk.webhooks.verify_and_parse(raw_body, public_key_pem)
print(payload["event"], payload["status"])
```

Signature verification:

- Builds a canonical string by sorting all keys except `signature` and joining `key=value` with `&`.
- Verifies an RSA‑SHA256 signature using the LakiPay public key (PEM).

---

### 5. Data Models

The SDK request/response bodies follow the same fields as the core LakiPay API:

- Request types:
  - Direct payment
  - Withdrawal
  - Hosted checkout
- Response envelope:
  - `status`: `"SUCCESS"` or `"ERROR"`
  - `message`: human‑readable message
  - `data`: transaction / checkout details
  - `error_code`: optional machine‑readable code
  - `errors`: optional field‑level validation errors

Refer to the main API documentation for full field definitions.

---


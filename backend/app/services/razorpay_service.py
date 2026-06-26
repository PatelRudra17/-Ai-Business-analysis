"""Razorpay payment integration — uses httpx directly (no razorpay SDK needed)."""
import hashlib
import hmac

import httpx

from app.config import settings

PRODUCTS = {
    "single_report":  {"amount_paise": 99900,  "label": "Single Location Report"},
    "comparison":     {"amount_paise": 199900, "label": "Two-Location Comparison"},
    "monitoring_1m":  {"amount_paise": 299900, "label": "1-Month Monitoring Plan"},
    "monitoring_12m": {"amount_paise": 299900 * 10, "label": "Annual Monitoring Plan"},
}

_RAZORPAY_BASE = "https://api.razorpay.com/v1"


def _auth() -> tuple[str, str]:
    return (settings.RAZORPAY_KEY_ID, settings.RAZORPAY_KEY_SECRET)


def create_order(product: str, analysis_id: str, user_email: str) -> dict:
    if product not in PRODUCTS:
        raise ValueError(f"Unknown product: {product}")
    p = PRODUCTS[product]
    payload = {
        "amount": p["amount_paise"],
        "currency": "INR",
        "receipt": f"blip_{analysis_id[:8]}",
        "notes": {
            "analysis_id": analysis_id,
            "product": product,
            "user_email": user_email,
        },
    }
    resp = httpx.post(f"{_RAZORPAY_BASE}/orders", json=payload, auth=_auth(), timeout=15)
    resp.raise_for_status()
    order = resp.json()
    return {
        "order_id": order["id"],
        "amount_paise": p["amount_paise"],
        "amount_inr": p["amount_paise"] / 100,
        "currency": "INR",
        "product": product,
        "label": p["label"],
        "key_id": settings.RAZORPAY_KEY_ID,
    }


def verify_payment_signature(order_id: str, payment_id: str, signature: str) -> bool:
    body = f"{order_id}|{payment_id}"
    expected = hmac.new(
        settings.RAZORPAY_KEY_SECRET.encode(),
        body.encode(),
        hashlib.sha256,
    ).hexdigest()
    return hmac.compare_digest(expected, signature)

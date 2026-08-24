"""Razorpay.

**Why hosted pages rather than the native SDK.** Razorpay's usual React Native
integration is `react-native-razorpay`, a native module — which would mean this
app can no longer be run in Expo Go, and every contributor needs a development
build before they can open the chat screen. Payment Links and the hosted
subscription page are ordinary URLs. The app opens one in a browser, the person
pays with UPI or a card, and the browser returns them to a deep link. Nothing
native, and the checkout page is maintained by Razorpay rather than by us.

**The client never names a price.** It asks for a plan id; the amount is read
from `plans.py` on this side. A checkout endpoint that accepts an amount from
the device is a checkout endpoint that sells a yearly subscription for one
rupee.

**Truth arrives by webhook, not by the browser coming back.** The redirect
after payment is a convenience for the person looking at the screen — it can be
lost to a closed tab, a dead battery or a browser that decided not to follow
it. Credits are granted from the signed webhook, which Razorpay retries. The
app polls its balance after returning, so the common case still feels
immediate.
"""

from __future__ import annotations

import hashlib
import hmac
import os
from typing import Any

import httpx

from .. import config  # noqa: F401  — loads .env before os.environ is read
from . import plans

API = "https://api.razorpay.com/v1"

KEY_ID = os.environ.get("RAZORPAY_KEY_ID", "").strip()
KEY_SECRET = os.environ.get("RAZORPAY_KEY_SECRET", "").strip()
WEBHOOK_SECRET = os.environ.get("RAZORPAY_WEBHOOK_SECRET", "").strip()

#: Where the browser is sent after paying. A deep link back into the app, so
#: the person lands on the screen they left rather than on a Razorpay receipt.
CALLBACK_URL = os.environ.get("BILLING_CALLBACK_URL", "").strip()

TIMEOUT = httpx.Timeout(15.0, connect=5.0)

#: How many times a subscription may be charged before Razorpay marks it
#: completed. Razorpay requires a finite count, so these are "long enough that
#: nobody reaches them" rather than meaningful limits.
TOTAL_COUNT = {"monthly": 120, "yearly": 10}


class GatewayError(RuntimeError):
    """Razorpay refused, or could not be reached."""


def is_configured() -> bool:
    return bool(KEY_ID and KEY_SECRET)


def _post(path: str, body: dict[str, Any]) -> dict[str, Any]:
    if not is_configured():
        raise GatewayError("Razorpay is not configured on this server")

    try:
        response = httpx.post(
            f"{API}{path}", json=body, auth=(KEY_ID, KEY_SECRET), timeout=TIMEOUT
        )
    except httpx.HTTPError as exc:
        raise GatewayError(f"Could not reach Razorpay: {exc}") from exc

    if response.status_code >= 400:
        # Razorpay's error bodies are informative and safe to log, but the
        # description can name internal configuration, so callers surface a
        # generic message and keep this for the server's own logs.
        raise GatewayError(f"Razorpay refused ({response.status_code}): {response.text[:300]}")

    return response.json()


# --- Buying --------------------------------------------------------------


def create_pack_link(plan: plans.Plan, user_id: str, email: str | None) -> dict[str, str]:
    """A one-time Payment Link for a credit pack.

    `notes` is the only thing that survives the round trip to the webhook, so
    it carries everything the grant will need: whose account, and which pack.
    Reading the plan back out of notes rather than from the amount means a
    price change tomorrow cannot misgrant a link bought today.
    """
    body: dict[str, Any] = {
        "amount": plan.amount_paise,
        "currency": "INR",
        "accept_partial": False,
        "description": f"Kosmiq — {plan.label}",
        "notes": {"user_id": user_id, "plan_id": plan.id},
        "notify": {"sms": False, "email": bool(email)},
        "reminder_enable": False,
    }
    if email:
        body["customer"] = {"email": email}
    if CALLBACK_URL:
        body["callback_url"] = CALLBACK_URL
        body["callback_method"] = "get"

    created = _post("/payment_links", body)
    return {"id": str(created["id"]), "url": str(created["short_url"])}


def create_subscription(plan: plans.Plan, user_id: str, email: str | None) -> dict[str, str]:
    """A recurring subscription, returned as a hosted page to open.

    The mandate — UPI Autopay or a card e-mandate — is set up on that page. It
    is why a subscription cannot be a Payment Link: a link takes one payment,
    and what is wanted here is permission to take the next one.
    """
    razorpay_plan = plans.razorpay_plan_id(plan)
    if not razorpay_plan:
        raise GatewayError(f"No Razorpay plan configured for {plan.id}")

    body: dict[str, Any] = {
        "plan_id": razorpay_plan,
        "total_count": TOTAL_COUNT.get(plan.period or "monthly", 12),
        "customer_notify": 1,
        "notes": {"user_id": user_id, "plan_id": plan.id},
    }
    if email:
        body["notify_info"] = {"notify_email": email}

    created = _post("/subscriptions", body)
    return {"id": str(created["id"]), "url": str(created["short_url"])}


def cancel_subscription(provider_id: str, at_period_end: bool = True) -> dict[str, Any]:
    """Stop a subscription, by default at the end of what has been paid for.

    Cancelling immediately would take back time someone has already bought.
    The credits granted for the current month are left alone either way; they
    expire on their own when the month does.
    """
    return _post(
        f"/subscriptions/{provider_id}/cancel",
        {"cancel_at_cycle_end": 1 if at_period_end else 0},
    )


# --- Webhooks ------------------------------------------------------------


def verify_webhook(body: bytes, signature: str | None) -> bool:
    """Whether this request really came from Razorpay.

    The signature is over the raw bytes, which is why the route reads
    `await request.body()` and parses the JSON itself: re-serialising a parsed
    body produces different bytes and a signature that never matches.

    `compare_digest` rather than `==` — the comparison is against a secret, and
    the timing of a byte-by-byte mismatch is information.
    """
    if not WEBHOOK_SECRET or not signature:
        return False

    expected = hmac.new(WEBHOOK_SECRET.encode("utf-8"), body, hashlib.sha256).hexdigest()
    return hmac.compare_digest(expected, signature.strip())

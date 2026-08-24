"""The service-role side of Supabase.

Everything in this module runs with a key that bypasses row-level security, so
it lives behind one door: a caller has to have been identified by
`app.auth.require_user` before anything here is reached. Nothing in this file
takes a user id from a request body.

**Why HTTP and not a Postgres driver.** The functions this calls are the whole
interface — `consume_credit`, `grant_credits`, `record_payment` — and PostgREST
already exposes them. A driver would add a connection pool to manage on a free
instance that sleeps, for no query this file wants to write.

**Configuration decides whether billing exists at all.** With no Supabase
service key the module reports itself disabled and the endpoints fall back to
their old, open behaviour. That is deliberate: the app is designed to run
against a backend with no Supabase project at all, and a developer running the
engine locally should not have to stand up billing to ask a question.
"""

from __future__ import annotations

import os
from typing import Any

import httpx

from .. import config  # noqa: F401  — loads .env before os.environ is read

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")
SERVICE_KEY = os.environ.get("SUPABASE_SERVICE_ROLE_KEY", "").strip()

TIMEOUT = httpx.Timeout(10.0, connect=5.0)


class StoreError(RuntimeError):
    """Supabase could not be reached, or refused what it was asked."""


def is_configured() -> bool:
    """Whether this deployment can charge for anything."""
    return bool(SUPABASE_URL and SERVICE_KEY)


def _headers() -> dict[str, str]:
    return {
        "apikey": SERVICE_KEY,
        "Authorization": f"Bearer {SERVICE_KEY}",
        "Content-Type": "application/json",
    }


def rpc(name: str, payload: dict[str, Any]) -> Any:
    """Call one Postgres function and return whatever it returned.

    Errors are raised rather than swallowed. A credit call that quietly fails
    is worse than one that 500s: the first sells a message that was never paid
    for, or charges for one that was never sent.
    """
    if not is_configured():
        raise StoreError("Supabase is not configured on this server")

    url = f"{SUPABASE_URL}/rest/v1/rpc/{name}"
    try:
        response = httpx.post(url, json=payload, headers=_headers(), timeout=TIMEOUT)
    except httpx.HTTPError as exc:
        raise StoreError(f"Could not reach Supabase: {exc}") from exc

    if response.status_code >= 400:
        raise StoreError(f"{name} failed ({response.status_code}): {response.text[:200]}")

    if not response.content:
        return None
    return response.json()


def select(table: str, params: dict[str, str]) -> list[dict[str, Any]]:
    """Read rows with the service role.

    Only used where the backend needs to check a fact before acting on it —
    chiefly "does this subscription belong to the person asking to cancel it".
    Row-level security does not apply to this key, so every caller supplies its
    own `user_id` filter and none of them take one from a request body.
    """
    if not is_configured():
        raise StoreError("Supabase is not configured on this server")

    try:
        response = httpx.get(
            f"{SUPABASE_URL}/rest/v1/{table}",
            params=params,
            headers=_headers(),
            timeout=TIMEOUT,
        )
    except httpx.HTTPError as exc:
        raise StoreError(f"Could not reach Supabase: {exc}") from exc

    if response.status_code >= 400:
        raise StoreError(f"select {table} failed ({response.status_code}): {response.text[:200]}")

    rows = response.json()
    return rows if isinstance(rows, list) else []


def live_subscription(user_id: str) -> dict[str, Any] | None:
    """This account's subscription, if it has one that is still running."""
    rows = select(
        "subscriptions",
        {
            "user_id": f"eq.{user_id}",
            "status": "in.(created,authenticated,active,pending,halted)",
            "select": "id,plan,status,provider_id,current_period_end",
            "order": "created_at.desc",
            "limit": "1",
        },
    )
    return rows[0] if rows else None


# --- Credits ----------------------------------------------------------------


def consume_credit(user_id: str, ref: str) -> tuple[bool, int]:
    """Spend one credit. Returns (allowed, balance after).

    `ref` is the idempotency key and must identify the *request*, not the
    account: the same ref twice spends once, which is what makes a retry after
    a dropped stream free rather than punitive.
    """
    result = rpc("consume_credit", {"p_user_id": user_id, "p_ref": ref})
    if not isinstance(result, dict):
        raise StoreError(f"consume_credit returned {type(result).__name__}, expected an object")
    return bool(result.get("ok")), int(result.get("balance") or 0)


def refund_credit(user_id: str, ref: str) -> bool:
    """Give back a credit charged for something that then failed on our side.

    Called when the model never produced an answer. Someone whose question was
    swallowed by a 503 has not spent anything, and should not be told they have.
    """
    return bool(rpc("refund_credit", {"p_user_id": user_id, "p_ref": ref}))


def grant_credits(
    user_id: str,
    credits: int,
    source: str,
    source_ref: str,
    expires_at: str | None = None,
) -> str | None:
    """Add a lot. Returns its id, or None when `source_ref` was already used.

    None is the ordinary answer to a webhook Razorpay delivered twice, not a
    failure — the caller treats it as success.
    """
    return rpc(
        "grant_credits",
        {
            "p_user_id": user_id,
            "p_credits": credits,
            "p_source": source,
            "p_source_ref": source_ref,
            "p_expires_at": expires_at,
        },
    )


def ensure_grants(user_id: str) -> None:
    """Mint anything this account is owed but has not been given yet.

    Normally this happens by itself when the app reads its balance. The webhook
    calls it too, so that credits are already sitting there when someone
    returns from the payment page rather than appearing on the next refresh.
    """
    rpc("ensure_grants", {"p_user_id": user_id})


# --- Subscriptions and payments ---------------------------------------------


def record_subscription(
    user_id: str,
    plan: str,
    status: str,
    provider_id: str,
    period_end: str | None = None,
) -> None:
    rpc(
        "record_subscription",
        {
            "p_user_id": user_id,
            "p_plan": plan,
            "p_status": status,
            "p_provider_id": provider_id,
            "p_period_end": period_end,
        },
    )


def record_payment(
    user_id: str,
    payment_id: str,
    order_id: str | None,
    product: str,
    amount_paise: int,
    status: str,
) -> None:
    rpc(
        "record_payment",
        {
            "p_user_id": user_id,
            "p_payment_id": payment_id,
            "p_order_id": order_id,
            "p_product": product,
            "p_amount": amount_paise,
            "p_status": status,
        },
    )

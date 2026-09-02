"""Who has paid.

This replaces the credit ledger. The old model sold a currency — six free a
day, packs bought outright, a month's worth from a subscription — and spent it
one message at a time. It is gone, along with `app.billing`, `credit_lots`,
`credit_spends` and the client-supplied idempotency key that turned out to make
the whole paywall optional (the same `request_id` twice was charged once, so
the same `request_id` forever was charged once ever).

What is left is a single question: **is `kosmiq_pro` active on this account.**
Nothing is metered, nothing expires at midnight, and there is no number for a
modified client to argue with.

**Why the store and not our own gateway.** Apple and Google both require that
digital goods consumed inside an app are sold through their billing, so the
subscription is a StoreKit or Play Billing purchase, brokered by RevenueCat.
Razorpay's hosted pages were the right answer while this was a web product and
are the wrong one now; they are deleted rather than left switched off.

**Why this asks RevenueCat rather than trusting the device.** The app already
knows whether it is Pro — `src/purchases/context.tsx` reads it from the SDK —
and that knowledge is good enough to decide what a screen draws. It is not good
enough to decide what this server gives away, because a rooted phone can say
anything and the answer costs real model tokens. So the entitlement is read
here, from RevenueCat's own API, with the secret key that never leaves the
backend.

**Why a query and not a webhook.** A webhook would mean a table to keep, an
endpoint to secure, and a window after every purchase in which the database
disagrees with the store. RevenueCat's subscriber endpoint *is* the source of
truth, one HTTP call away, and the cache below collapses a burst of messages
into one lookup a minute. Against a model request measured in seconds, it does
not register. It is the same shape as `auth.py`, for the same reasons.

**Failure is closed.** An unreachable RevenueCat is a 503, not a free message —
this is the door the money is behind. The one deliberate exception is a
deployment with no RevenueCat key at all, which is how the engine runs locally:
there, nothing is for sale and nothing is gated, and `is_configured()` says so
out loud at startup rather than being discovered in production.
"""

from __future__ import annotations

import datetime as dt
import logging
import os
import threading
import time
from urllib.parse import quote

import httpx
from fastapi import Depends, HTTPException

from . import auth, config  # noqa: F401  — config loads .env before os.environ

log = logging.getLogger("kosmiq.entitlements")

API = "https://api.revenuecat.com/v1"

#: The secret half of RevenueCat. Its publishable siblings ship inside the app
#: binary; this one authorises reading any customer's subscription state and
#: must never appear in `mobile/.env`.
SECRET_KEY = os.environ.get("REVENUECAT_SECRET_KEY", "").strip()

#: The one entitlement this product gates on. Mirrored in
#: `mobile/src/purchases/config.ts` as `PRO_ENTITLEMENT` — two copies of a
#: string, and the only thing keeping them together is this comment and the one
#: there. Configurable so a rename can be rolled out without a release.
ENTITLEMENT = os.environ.get("REVENUECAT_ENTITLEMENT", "kosmiq_pro").strip() or "kosmiq_pro"

TIMEOUT = httpx.Timeout(8.0, connect=4.0)

#: How long an answer is trusted without asking again. Short enough that a
#: refund or an expiry stops working within the minute, long enough that a
#: conversation costs one lookup rather than one per message.
CACHE_TTL_SECONDS = 60

#: A bound, so a service being probed cannot grow this without limit.
CACHE_MAX = 4096


class Entitlement:
    """What RevenueCat says about one account.

    `expires_at` is None for a lifetime purchase *and* for no purchase at all,
    which is why nothing may read it without checking `active` first — the
    mistake this class exists to make hard to write.
    """

    __slots__ = ("active", "expires_at", "product")

    def __init__(
        self,
        active: bool,
        expires_at: dt.datetime | None = None,
        product: str | None = None,
    ) -> None:
        self.active = active
        self.expires_at = expires_at
        self.product = product


NOT_ENTITLED = Entitlement(active=False)

_cache: dict[str, tuple[Entitlement, float]] = {}
_lock = threading.Lock()


def is_configured() -> bool:
    """Whether this deployment can tell a subscriber from anyone else."""
    return bool(SECRET_KEY)


def _parse_expiry(value: object) -> dt.datetime | None:
    """RevenueCat's `2026-09-01T12:00:00Z` as an aware datetime.

    Returns None for a lifetime entitlement, which carries no expiry at all,
    and for anything unparseable — a date this code cannot read must not be
    treated as a date in the past, because that would revoke access over a
    formatting change on someone else's server.
    """
    if not isinstance(value, str) or not value:
        return None
    try:
        return dt.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError:
        log.warning("unparseable entitlement expiry: %r", value)
        return None


def _read(user_id: str) -> Entitlement:
    """Ask RevenueCat about one subscriber.

    The path segment is quoted because a Supabase user id is ours to trust but
    the function is not: an id is interpolated into a URL here, and the habit of
    escaping that is worth more than the argument that this particular id is
    always a UUID.
    """
    try:
        response = httpx.get(
            f"{API}/subscribers/{quote(user_id, safe='')}",
            headers={
                "Authorization": f"Bearer {SECRET_KEY}",
                "Accept": "application/json",
            },
            timeout=TIMEOUT,
        )
    except httpx.HTTPError as exc:
        # Not the same as "not subscribed", and the caller says so differently:
        # this is a 503, never a 402.
        raise HTTPException(
            status_code=503, detail=f"Could not check your subscription: {exc}"
        ) from exc

    # 404 means RevenueCat has never seen this account — someone who signed up
    # and has not bought anything. That is an answer, not an error.
    if response.status_code == 404:
        return NOT_ENTITLED

    if response.status_code == 401 or response.status_code == 403:
        # A wrong or revoked secret key. Refusing everyone is correct, but it
        # must be loud: this is a configuration failure wearing a paywall's
        # clothes, and it looks identical to "nobody has paid" from outside.
        log.error("RevenueCat rejected the secret key (%s)", response.status_code)
        raise HTTPException(status_code=503, detail="Could not check your subscription.")

    if response.status_code >= 400:
        log.warning("RevenueCat returned %s: %s", response.status_code, response.text[:200])
        raise HTTPException(status_code=503, detail="Could not check your subscription.")

    body = response.json()
    subscriber = body.get("subscriber")
    if not isinstance(subscriber, dict):
        return NOT_ENTITLED

    entitlements = subscriber.get("entitlements")
    if not isinstance(entitlements, dict):
        return NOT_ENTITLED

    granted = entitlements.get(ENTITLEMENT)
    if not isinstance(granted, dict):
        return NOT_ENTITLED

    expires_at = _parse_expiry(granted.get("expires_date"))
    # RevenueCat only lists an entitlement it has granted, but it lists expired
    # ones too, so the date is what decides. No date means lifetime.
    if expires_at is not None and expires_at <= dt.datetime.now(dt.timezone.utc):
        return NOT_ENTITLED

    product = granted.get("product_identifier")
    return Entitlement(
        active=True,
        expires_at=expires_at,
        product=product if isinstance(product, str) else None,
    )


def entitlement_of(user_id: str) -> Entitlement:
    """This account's Pro status, from cache when it is fresh."""
    now = time.monotonic()

    with _lock:
        hit = _cache.get(user_id)
        if hit and hit[1] > now:
            return hit[0]

    result = _read(user_id)

    with _lock:
        if len(_cache) >= CACHE_MAX:
            # Nothing clever. The cache exists to collapse a burst, and the
            # cheapest correct response to a full one is to start again.
            _cache.clear()
        _cache[user_id] = (result, now + CACHE_TTL_SECONDS)

    return result


def forget(user_id: str) -> None:
    """Drop a cached answer, so the next read goes to RevenueCat.

    For the moment after a purchase, when the app asks the server to confirm
    what the store has just told it and a minute of staleness would show a
    paying subscriber their paywall.
    """
    with _lock:
        _cache.pop(user_id, None)


def require_pro(account: auth.Account | None = Depends(auth.optional_user)) -> auth.Account | None:
    """FastAPI dependency: the caller, proven to be a subscriber.

    Three distinguishable failures, on purpose. Not signed in is 401 and means
    "sign in"; signed in without a subscription is 402 and means "here is the
    paywall"; RevenueCat unreachable is 503 and means "this is our fault, try
    again". One status for all three would leave the app guessing which screen
    to show, and would tell a subscriber their payment did not work.

    Returns None only on a deployment with no RevenueCat key, where nothing is
    for sale and so nothing is gated — that is what lets the engine be run
    locally without standing up billing.
    """
    if not is_configured():
        return account

    if account is None:
        raise HTTPException(status_code=401, detail="Sign in to continue.")

    if not entitlement_of(account.id).active:
        raise HTTPException(
            status_code=402,
            detail="Kosmiq Pro is needed for this. Start a plan to continue.",
        )

    return account

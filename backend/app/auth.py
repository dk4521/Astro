"""Who is asking.

Until now the backend was stateless in the strong sense: it had never been told
who was on the other end, and `/v1/chat` answered anyone who could reach it.
That was fine while the allowance was advisory. It stops being fine the moment
an answer costs money, because the app deciding whether to send is not
enforcement — it is a request, and a modified client is not obliged to honour
it.

Identity is half the door. The other half is `entitlements.py`, which asks
whether this person has paid; neither is any use without the other.

**How the token is checked, and why not locally.** The obvious approach is to
verify the JWT's signature here with the project's secret. It is also the one
that breaks quietly: Supabase now issues asymmetric signing keys and rotates
them, so local verification means fetching a JWKS, caching it, and handling the
rotation that happens without warning. Asking Supabase who the token belongs to
is one HTTP call that is correct under every key type, present and future.

The cost of that call is one round trip per message, and it is paid at most
once a minute per person because of the cache below. Against a model request
that takes seconds, it does not register.

**Failure is closed, not open.** The app falls open when it cannot tell whether
someone is subscribed, and it is right to: being wrong on the device only draws
the wrong screen. Here the same wrongness gives away model requests to anyone
who can forge a token badly, so an unverifiable one is refused.
"""

from __future__ import annotations

import hashlib
import os
import threading
import time
from dataclasses import dataclass

import httpx
from fastapi import Header, HTTPException

from . import config  # noqa: F401  — loads .env before os.environ is read

SUPABASE_URL = os.environ.get("SUPABASE_URL", "").strip().rstrip("/")

# The `apikey` header on this endpoint, while the token in `Authorization` is
# what identifies the person. The service-role key used to be accepted here as a
# last resort; it is not any more. Nothing in this backend needs that key since
# the credit ledger was deleted, and a key that bypasses row-level security
# should not be reachable from a code path whose job is merely to read a name.
_API_KEY = (
    os.environ.get("SUPABASE_ANON_KEY", "").strip()
    or os.environ.get("SUPABASE_PUBLISHABLE_KEY", "").strip()
)

TIMEOUT = httpx.Timeout(8.0, connect=4.0)

#: How long a verified token is trusted without asking again. Short enough that
#: a deleted account stops working within the minute, long enough that a burst
#: of messages costs one verification.
CACHE_TTL_SECONDS = 60

#: A bound, so a service being probed with junk tokens cannot grow this without
#: limit. Tokens are hashed before they are used as keys — an access token is a
#: credential, and a process dump should not be a list of them.
CACHE_MAX = 2048

@dataclass(frozen=True)
class Account:
    """Everything about the caller this backend has any use for."""

    id: str
    #: Carried so a receipt can be addressed. Supabase accounts created by
    #: phone or by an anonymous sign-in have none, so it is optional and
    #: nothing may depend on it.
    email: str | None


_cache: dict[str, tuple[Account, float]] = {}
_lock = threading.Lock()


def is_configured() -> bool:
    """Whether this deployment can identify anyone at all."""
    return bool(SUPABASE_URL and _API_KEY)


def _bearer(header: str | None) -> str | None:
    if not header:
        return None
    scheme, _, token = header.partition(" ")
    if scheme.lower() != "bearer":
        return None
    return token.strip() or None


def _verify(token: str) -> Account | None:
    """The account this token belongs to, or None if it belongs to nobody."""
    key = hashlib.sha256(token.encode("utf-8")).hexdigest()
    now = time.monotonic()

    with _lock:
        hit = _cache.get(key)
        if hit and hit[1] > now:
            return hit[0]

    try:
        response = httpx.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={"apikey": _API_KEY, "Authorization": f"Bearer {token}"},
            timeout=TIMEOUT,
        )
    except httpx.HTTPError as exc:
        # Not the same as an invalid token, and the caller says so differently:
        # this is a 503, not a 401.
        raise HTTPException(
            status_code=503, detail=f"Could not verify the session: {exc}"
        ) from exc

    if response.status_code != 200:
        return None

    body = response.json()
    user_id = body.get("id")
    if not isinstance(user_id, str) or not user_id:
        return None

    email = body.get("email")
    account = Account(id=user_id, email=email if isinstance(email, str) and email else None)

    with _lock:
        if len(_cache) >= CACHE_MAX:
            # Nothing clever. The cache exists to collapse a burst, and the
            # cheapest correct response to a full one is to start again.
            _cache.clear()
        _cache[key] = (account, now + CACHE_TTL_SECONDS)

    return account


def require_user(authorization: str | None = Header(default=None)) -> Account:
    """FastAPI dependency: the caller's account, or 401.

    Used on endpoints that spend money. It refuses rather than degrades — an
    endpoint that charges must know who it is charging.
    """
    if not is_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Accounts are not configured on this server. Set SUPABASE_URL "
                "and SUPABASE_ANON_KEY (see backend/.env.example)."
            ),
        )

    token = _bearer(authorization)
    if not token:
        raise HTTPException(status_code=401, detail="Sign in to continue.")

    account = _verify(token)
    if not account:
        raise HTTPException(status_code=401, detail="Your session has expired. Sign in again.")

    return account


def optional_user(authorization: str | None = Header(default=None)) -> Account | None:
    """The caller's account when there is one, without insisting.

    For endpoints that must keep working on a deployment with no Supabase
    project — the whole app runs that way in development, and refusing to cast
    a chart because nobody configured accounts would be absurd. Also for
    `entitlements.require_pro`, which needs to tell "signed out" (401) from
    "signed in without a plan" (402) and so must be handed the None itself.
    """
    if not is_configured():
        return None

    token = _bearer(authorization)
    if not token:
        return None

    try:
        return _verify(token)
    except HTTPException:
        return None

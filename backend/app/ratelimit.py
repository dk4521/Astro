"""A brake, not a quota.

The service had no rate limiting of any kind. Every endpoint was reachable as
fast as a client could ask, which mattered in three different ways: `/v1/places`
runs a linear scan over three thousand rows on every keystroke, the AI endpoints
spend real money per call, and `/v1/chat` holds a streaming connection open for
seconds at a time.

**Fixed windows, in memory, per process.** Deliberately the simple thing, and
worth being honest about what that costs: two instances behind a load balancer
allow twice these numbers, and a restart forgives everyone. Neither matters for
what this is for. The limits below are set where a human being cannot reach them
and a script reaches them immediately, so an approximation in the generous
direction still catches the case that matters. A Redis-backed limiter is the
upgrade when there is a second instance to share state with — not before, and
`app.ai.cache` already carries the same caveat.

**The identity is the account where there is one.** An IP is a poor identity —
carrier-grade NAT puts a city behind one address, and a phone changes address
walking between two cells — so it is used only where there is nothing better.
Anything behind `require_pro` is keyed on the user id instead, which is exact.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass, field

from fastapi import HTTPException, Request


@dataclass
class Window:
    """One fixed-window limiter.

    `limit` requests per `seconds`, counted per key. A window starts at the
    first request that lands in it rather than on a wall-clock boundary, so a
    burst does not get to straddle a boundary and pass twice.
    """

    limit: int
    seconds: float
    #: key -> (count, window started at). Bounded by `_sweep`, which is what
    #: keeps a stream of one-request-each callers from growing this forever.
    _hits: dict[str, tuple[int, float]] = field(default_factory=dict)
    _lock: threading.Lock = field(default_factory=threading.Lock)
    _swept_at: float = 0.0

    def _sweep(self, now: float) -> None:
        """Drop windows that have closed. Caller holds the lock."""
        if now - self._swept_at < self.seconds:
            return
        self._swept_at = now
        self._hits = {
            key: value for key, value in self._hits.items() if now - value[1] < self.seconds
        }

    def retry_after(self, key: str) -> int | None:
        """Count one request against `key`. None if it is allowed.

        Otherwise the honest number of seconds left in the window, so a
        well-behaved client can wait exactly that long instead of guessing.

        Non-raising because a Starlette middleware is one of the two callers and
        an `HTTPException` raised in one does not reach FastAPI's handler — it
        surfaces as a 500, which is the wrong thing to tell a client that is
        merely too fast.
        """
        now = time.monotonic()

        with self._lock:
            self._sweep(now)

            count, started = self._hits.get(key, (0, now))
            if now - started >= self.seconds:
                count, started = 0, now

            if count >= self.limit:
                return max(1, int(self.seconds - (now - started)) + 1)

            self._hits[key] = (count + 1, started)
            return None

    def check(self, key: str) -> None:
        """`retry_after`, as a 429 . For use inside a route or a dependency."""
        wait = self.retry_after(key)
        if wait is not None:
            raise HTTPException(
                status_code=429,
                detail="Too many requests. Slow down and try again.",
                headers={"Retry-After": str(wait)},
            )

    def reset(self) -> None:
        """Forget every window. For tests, which must not inherit each other's."""
        with self._lock:
            self._hits.clear()
            self._swept_at = 0.0


#: Everything, per address. High enough that the app's own onboarding screen —
#: which fires a place search every 250 ms while someone types — never sees it,
#: low enough that a scraper does.
GLOBAL = Window(limit=240, seconds=60.0)

#: The endpoints that call a model, per account. A person asks a question every
#: few seconds at most; twenty a minute is a script.
AI = Window(limit=20, seconds=60.0)

#: Sign-in and sign-up happen against Supabase directly, so the only thing this
#: service can protect is its own token verification — which it caches. Kept
#: separate anyway, because a burst of junk bearer tokens is a burst of
#: outbound requests to Supabase.
AUTH = Window(limit=30, seconds=60.0)


def client_key(request: Request) -> str:
    """The best available identity for an unauthenticated caller.

    `X-Forwarded-For` is trusted because this runs behind Render's proxy, which
    appends the real address; the first entry is the client. It is also
    forgeable by anyone talking to the origin directly, which is the standing
    argument for keying on an account wherever there is one — and the reason
    this limit is a brake on accidents rather than a defence against a
    determined attacker.
    """
    forwarded = request.headers.get("x-forwarded-for", "")
    if forwarded:
        first = forwarded.split(",")[0].strip()
        if first:
            return first

    client = request.client
    return client.host if client else "unknown"


def reset_all() -> None:
    """Clear every limiter. Used by the test suite between cases."""
    for window in (GLOBAL, AI, AUTH):
        window.reset()

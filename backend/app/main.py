"""FastAPI application entry point."""

from __future__ import annotations

import hmac
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from . import ai, auth, entitlements, ratelimit
from .api.billing import router as billing_router
from .api.routes import router
from .astro import EPHEMERIS_MODE

log = logging.getLogger("enumasky")


@asynccontextmanager
async def lifespan(_: FastAPI):
    """Say out loud which of the two switches are off.

    Both fail silently and in the same direction — everything works, and nobody
    pays — so a deployment missing one looks exactly like a deployment that is
    fine. This used to be readable from `/health` by anyone who asked, which
    told an attacker whether the paywall was on before they bothered trying it.
    Now it is said once, to the server's own log, where it belongs.
    """
    accounts = auth.is_configured()
    paywall = entitlements.is_configured()

    if not accounts:
        log.warning("SUPABASE_URL/SUPABASE_ANON_KEY unset — nobody can be identified.")
    if not paywall:
        log.warning(
            "REVENUECAT_SECRET_KEY unset — every AI endpoint is open to anyone who "
            "can reach this server."
        )

    # The combination, called out separately because it is the one that looks
    # like a working deployment and is not. With a paywall and no way to
    # identify anyone, every caller is anonymous, so every AI endpoint answers
    # 401 — to subscribers too, who are signed in as far as their phone is
    # concerned and are told to sign in anyway. Neither warning above says that
    # on its own, and the symptom points at the app rather than at this.
    if paywall and not accounts:
        log.error(
            "MISCONFIGURED: REVENUECAT_SECRET_KEY is set but SUPABASE_URL/"
            "SUPABASE_ANON_KEY are not. Every AI endpoint will answer 401 for "
            "everyone, including paying subscribers. Set both, or unset the "
            "RevenueCat key to run without a paywall."
        )

    yield


app = FastAPI(
    title="Jyotish API",
    version="0.1.0",
    description=(
        "Deterministic Vedic astrology calculations. Every response is a pure "
        "function of the birth data supplied — no model output, no randomness."
    ),
    lifespan=lifespan,
)

# --- CORS -------------------------------------------------------------------
#
# This used to default to `*` with a comment saying it must be narrowed before
# launch, which is a comment that never wins an argument with a release date.
# It now defaults to the two origins a developer actually needs — Expo's web
# preview on localhost — and nothing else. A native app is not a browser and
# sends no Origin header, so the phone is unaffected either way; CORS only ever
# governed `expo start --web`.
#
# `*` is still reachable by setting CORS_ORIGINS to it explicitly, because a
# deployment that has thought about it is allowed to. The difference is that it
# is now a decision someone made rather than one nobody unmade.
_DEV_ORIGINS = "http://localhost:8081,http://localhost:19006"

_configured = os.environ.get("CORS_ORIGINS", "").strip()
_origins = [o.strip() for o in (_configured or _DEV_ORIGINS).split(",") if o.strip()]

if _configured == "*":
    log.warning("CORS_ORIGINS is '*' — every website may call this API from a browser.")

app.add_middleware(
    CORSMiddleware,
    allow_origins=_origins,
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)


@app.middleware("http")
async def _rate_limit(request: Request, call_next):
    """One ceiling over everything, per address.

    Deliberately outside the router so it also covers the endpoints that take no
    dependencies — `/health`, the OpenAPI schema, and every deterministic
    calculation. The per-account limit on the endpoints that spend money is a
    separate and much lower one; see `app.ratelimit`.
    """
    if request.method == "OPTIONS":
        # A preflight is the browser's own question and never a load worth
        # counting; refusing one breaks the request that follows it.
        return await call_next(request)

    wait = ratelimit.GLOBAL.retry_after(ratelimit.client_key(request))
    if wait is not None:
        return JSONResponse(
            status_code=429,
            content={"detail": "Too many requests. Slow down and try again."},
            headers={"Retry-After": str(wait)},
        )

    return await call_next(request)


app.include_router(router, prefix="/v1")
app.include_router(billing_router, prefix="/v1")


@app.get("/health", summary="Liveness and ephemeris provenance")
def health() -> dict[str, object]:
    """Deliberately boring.

    It used to report whether accounts, credits and payments were configured,
    plus the interpretation cache's hit ratio. That was genuinely useful and it
    was also an unauthenticated answer to "is the paywall switched on, and how
    warm is the cache" — so the configuration moved to the startup log above,
    and the cache stats to `/v1/health/cache`, which needs a key.
    """
    return {
        "status": "ok",
        "ephemeris_mode": EPHEMERIS_MODE,
        "ayanamsa": "Lahiri (Chitrapaksha)",
    }


#: Set to read `/v1/health/cache`. Unset, the endpoint 404s like any other path
#: that is not there — an operator's tool should not announce itself.
_METRICS_TOKEN = os.environ.get("METRICS_TOKEN", "").strip()


@app.get("/v1/health/cache", summary="Interpretation cache reuse", include_in_schema=False)
def cache_stats(token: str = "") -> dict[str, object]:
    """Cache reuse, for whoever is paying the model bill.

    Worth watching rather than assuming: the free tier allows twenty requests
    per model per day, so `ratio` is the number that says whether the service
    can survive its own users. It resets when the process does — the cache is in
    memory, and on a free instance that means every cold start.
    """
    # `compare_digest` because the comparison is against a secret and the timing
    # of a byte-by-byte mismatch is information — the same reason the Razorpay
    # webhook used it, kept now that it is the only secret compared here.
    if not _METRICS_TOKEN or not hmac.compare_digest(token, _METRICS_TOKEN):
        raise HTTPException(status_code=404, detail="Not Found")

    stats = ai.cache.stats()
    return {
        "hits": stats.hits,
        "misses": stats.misses,
        "entries": stats.entries,
        "capacity": stats.capacity,
        "ratio": round(stats.ratio, 3),
    }

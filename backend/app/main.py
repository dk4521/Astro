"""FastAPI application entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import ai
from .api.routes import router
from .astro import EPHEMERIS_MODE

app = FastAPI(
    title="Jyotish API",
    version="0.1.0",
    description=(
        "Deterministic Vedic astrology calculations. Every response is a pure "
        "function of the birth data supplied — no model output, no randomness."
    ),
)

# Expo talks to this from a device on the LAN and from the dev tunnel, so
# origins are configured rather than hard-coded. Defaults are wide open for
# local development and must be narrowed before launch.
_origins = os.environ.get("CORS_ORIGINS", "*").split(",")

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in _origins if o.strip()],
    allow_credentials=False,
    allow_methods=["GET", "POST"],
    allow_headers=["*"],
)

app.include_router(router, prefix="/v1")


@app.get("/health", summary="Liveness, ephemeris provenance, and cache reuse")
def health() -> dict[str, object]:
    """Also the only window onto the interpretation cache.

    Worth watching rather than assuming: the free tier allows 20 requests per
    model per day, so `ratio` is the number that says whether the service can
    survive its own users. It resets when the process does — the cache is in
    memory, and on a free instance that means every cold start.
    """
    stats = ai.cache.stats()
    return {
        "status": "ok",
        "ephemeris_mode": EPHEMERIS_MODE,
        "ayanamsa": "Lahiri (Chitrapaksha)",
        "cache": {
            "hits": stats.hits,
            "misses": stats.misses,
            "entries": stats.entries,
            "capacity": stats.capacity,
            "ratio": round(stats.ratio, 3),
        },
    }

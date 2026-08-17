"""FastAPI application entry point."""

from __future__ import annotations

import os

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

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


@app.get("/health", summary="Liveness and ephemeris provenance")
def health() -> dict[str, str]:
    return {
        "status": "ok",
        "ephemeris_mode": EPHEMERIS_MODE,
        "ayanamsa": "Lahiri (Chitrapaksha)",
    }

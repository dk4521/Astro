"""Reusing an answer the model has already given.

The free tier allows **20 requests per model per day**, which our own testing
exhausted in a single evening. Caching is therefore not an optimisation here; it
is the difference between an app that can serve a person and one that cannot.

The key is a hash of the entire request — every message, the system instruction,
the language directive, the model chain and the sampling settings. That choice
is what makes the cache honest: it cannot serve an answer that was produced from
different facts or a different prompt, because different facts and different
prompts hash differently. Nothing has to remember to invalidate anything.

It also gives the right lifetime for free. The fact brief carries `as of:` at
day precision (`facts.dasha_facts`), so tomorrow's request for the same chart
hashes differently and misses on its own. The TTL below is a memory bound, not a
correctness device — an entry that outlives its day is already unreachable.

**This cache does not survive a restart.** On Render's free tier the instance
spins down when idle, so a cold start starts cold. Stating that plainly matters:
the layer that actually protects a real user's quota is the one on the device
(`mobile/src/api/reading.ts`), which survives everything. This one earns its
keep within a warm process — repeated opens, language switches, two phones on
the same chart — and it is the only place a second user with an identical
request can be served for free.
"""

from __future__ import annotations

import hashlib
import json
import os
import threading
import time
from collections import OrderedDict
from dataclasses import dataclass

from .client import Request, cache_fingerprint

# 0 disables the cache entirely, which is the switch to reach for when a reading
# looks wrong and you need to know whether you are debugging the model or a
# stored answer.
SIZE = int(os.environ.get("ASTRO_CACHE_SIZE", "512"))

# A day and a bit. The slack is deliberate: an entry that expires exactly on the
# day boundary would be evicted at the moment the brief changes anyway, so the
# extra hours cost nothing and cover a request made a minute before midnight.
TTL_SECONDS = float(os.environ.get("ASTRO_CACHE_TTL", str(26 * 3600)))


@dataclass(frozen=True, slots=True)
class Stats:
    hits: int
    misses: int
    stored: int
    entries: int
    capacity: int

    @property
    def ratio(self) -> float:
        """Share of lookups served from the cache, 0.0 when there were none."""
        total = self.hits + self.misses
        return self.hits / total if total else 0.0


_lock = threading.Lock()
_entries: "OrderedDict[str, tuple[float, str]]" = OrderedDict()
_hits = 0
_misses = 0
_stored = 0


def key_for(request: Request) -> str:
    """A stable fingerprint of everything that can change the answer.

    `json.dumps` with sorted keys rather than `repr` or `hash`: dict ordering and
    Python's salted string hashing both vary between runs, and a key that changes
    when the process restarts is not a key.
    """
    payload = json.dumps(
        {
            "messages": request.messages,
            "suffix": request.suffix,
            "max_tokens": request.max_tokens,
            "model": cache_fingerprint(),
        },
        sort_keys=True,
        ensure_ascii=False,
        default=str,
    )
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def get(request: Request) -> str | None:
    """The stored answer for this exact request, or None."""
    global _hits, _misses

    if SIZE <= 0:
        return None

    key = key_for(request)
    now = time.monotonic()

    with _lock:
        entry = _entries.get(key)
        if entry is None:
            _misses += 1
            return None

        expires_at, text = entry
        if expires_at <= now:
            # Expired entries are dropped on the way past rather than by a
            # sweeper: nothing here runs on a timer, and a cache this small does
            # not need one.
            del _entries[key]
            _misses += 1
            return None

        _entries.move_to_end(key)
        _hits += 1
        return text


def put(request: Request, text: str) -> None:
    """Store an answer. Empty text is not stored — that is a failure, not a reply."""
    global _stored

    if SIZE <= 0 or not text.strip():
        return

    key = key_for(request)

    with _lock:
        _entries[key] = (time.monotonic() + TTL_SECONDS, text)
        _entries.move_to_end(key)
        _stored += 1
        while len(_entries) > SIZE:
            _entries.popitem(last=False)


def clear() -> None:
    """Empty the cache and reset the counters. Used by tests and by `/health`."""
    global _hits, _misses, _stored

    with _lock:
        _entries.clear()
        _hits = _misses = _stored = 0


def stats() -> Stats:
    with _lock:
        return Stats(
            hits=_hits,
            misses=_misses,
            stored=_stored,
            entries=len(_entries),
            capacity=SIZE,
        )

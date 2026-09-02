"""Shared fixtures.

The interpretation cache is process-global, which is what makes it useful in a
server and a hazard in a test suite: two tests that build the same request would
otherwise share an answer, and the second would pass or fail on the first one's
stub. Both of those actually happened when the cache was introduced — one test
asserting on ungrounded text got the *previous* test's grounded reply.
"""

from __future__ import annotations

import pytest

from app import entitlements, ratelimit
from app.ai import cache


@pytest.fixture(autouse=True)
def _empty_interpretation_cache():
    """Every test starts with an empty cache and leaves one behind."""
    cache.clear()
    yield
    cache.clear()


@pytest.fixture(autouse=True)
def _fresh_rate_limits():
    """Rate limits are process-global for the same reason the cache is.

    A suite of two hundred tests against one TestClient shares an address, so
    without this the two hundredth would meet a 429 raised by the first — a
    failure that moves around as tests are added and reads as anything but its
    real cause.
    """
    ratelimit.reset_all()
    yield
    ratelimit.reset_all()


@pytest.fixture(autouse=True)
def _forget_entitlements():
    """No test inherits another's answer about who has paid."""
    entitlements._cache.clear()
    yield
    entitlements._cache.clear()

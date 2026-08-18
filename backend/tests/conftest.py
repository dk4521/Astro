"""Shared fixtures.

The interpretation cache is process-global, which is what makes it useful in a
server and a hazard in a test suite: two tests that build the same request would
otherwise share an answer, and the second would pass or fail on the first one's
stub. Both of those actually happened when the cache was introduced — one test
asserting on ungrounded text got the *previous* test's grounded reply.
"""

from __future__ import annotations

import pytest

from app.ai import cache


@pytest.fixture(autouse=True)
def _empty_interpretation_cache():
    """Every test starts with an empty cache and leaves one behind."""
    cache.clear()
    yield
    cache.clear()

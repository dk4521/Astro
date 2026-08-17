"""Jyotish backend.

`config` is imported first and for its side effect: it loads `.env` before any
module reads `os.environ` at import time — `app.ai.client` and
`app.astro.ephemeris` both do.
"""

from . import config as config  # noqa: F401  (imported for its side effect)

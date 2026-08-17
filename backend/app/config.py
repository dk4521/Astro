"""Environment loading.

Imported for its side effect before anything reads `os.environ`, so a `.env`
file in the backend directory works the way people expect it to. Real
environment variables always win — a deployment's dashboard settings must not
be silently overridden by a stray `.env` that got into an image.
"""

from __future__ import annotations

from pathlib import Path

from dotenv import load_dotenv

ENV_FILE = Path(__file__).resolve().parent.parent / ".env"

# override=False: an already-set variable is left alone.
load_dotenv(ENV_FILE, override=False)

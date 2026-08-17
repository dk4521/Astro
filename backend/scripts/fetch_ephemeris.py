"""Download the JPL ephemeris kernel.

Run at build time so the first user request is not waiting on a 32 MB
download. Idempotent — skips the download if the kernel is already present.

    python scripts/fetch_ephemeris.py
"""

from __future__ import annotations

import sys

from app.astro import ephemeris as E


def main() -> int:
    target = E.EPHEMERIS_DIR / E.EPHEMERIS_FILE

    if target.exists():
        size_mb = target.stat().st_size / 1e6
        print(f"{target} already present ({size_mb:.1f} MB)")
        return 0

    print(f"downloading {E.EPHEMERIS_FILE} into {E.EPHEMERIS_DIR} …")
    E.EPHEMERIS_DIR.mkdir(parents=True, exist_ok=True)
    E._load_kernel()

    if not target.exists():
        print(f"error: {target} still missing after download", file=sys.stderr)
        return 1

    print(f"done ({target.stat().st_size / 1e6:.1f} MB)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

"""The course: thirty chapters, in English and Hindi.

Prose, not code. It lives here rather than in the mobile bundle for three
reasons: the app stays small, a correction ships without an app release, and the
personalised line at the end of each chapter is computed by the same engine that
draws the chart — see `personalise.py`.

The chapters themselves are in `parts/`, one module per part of the course; this
file only chains them into the single ordered tuple the API serves. Position in
that tuple is the chapter number the app displays, and several chapters refer to
each other by number, so reordering is not a free operation.

House style, worth keeping:

- **Positions are measurements.** Nothing here predicts, ranks a chart, or warns.
- **Say what the app actually does.** The conventions taught are this engine's —
  whole-sign houses, Lahiri, the mean node, a 365.25-day Vimshottari year, three
  dasha levels, the combustion orbs in chapter 12 — so a reader who finishes can
  check the arithmetic themselves.
- **Teach the misuse too.** Manglik, kaal sarp, sade sati and ashtakoot matching
  are named and explained rather than avoided, because a reader who can compute
  them is much harder to sell them.
- **Hindi is not a translation afterthought.** It is written, not rendered, and
  it is the version most of this market will read.
"""

from __future__ import annotations

from .models import Chapter
from .parts import cycles, foundations, grahas, houses, nakshatras, practice

CHAPTERS: tuple[Chapter, ...] = (
    foundations.CHAPTERS      # 1-5    what a chart is
    + grahas.CHAPTERS         # 6-12   the nine grahas
    + houses.CHAPTERS         # 13-18  the twelve houses
    + nakshatras.CHAPTERS     # 19-22  the twenty-seven nakshatras
    + cycles.CHAPTERS         # 23-27  dashas, transits, panchang
    + practice.CHAPTERS       # 28-30  divisions, limits, responsibility
)

CHAPTERS_BY_SLUG = {c.slug: c for c in CHAPTERS}

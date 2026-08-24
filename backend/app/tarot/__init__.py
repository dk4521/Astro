"""Tarot: a deck written by a person, dealt by a seed.

The same split the rest of this backend keeps. `deck` is the written material —
seventy-eight cards in two languages, no model involved, so it cannot be wrong
tomorrow in a way it was not wrong today. `spread` deals from it, reproducibly,
so a reading can be handed to someone else as a seed rather than as a screenshot.
`grounding` reads a generated reading back and checks it named only the cards
that were actually dealt.

What is *not* here is the model call. That lives in `reading.py`, one import
away, so the deck and the draw stay usable — and testable — with no key
configured and nothing to spend.
"""

from .deck import CARDS, CARDS_BY_ID, LANGUAGES, SUITS, SUITS_BY_ID, Card, Suit, pick
from .grounding import Uncalled
from .grounding import check as check_cards
from .spread import (
    POSITIONS,
    POSITIONS_BY_ID,
    SPREAD_NAME,
    SPREAD_NOTE,
    Draw,
    DrawnCard,
    Position,
    brief,
    draw,
    new_seed,
)

__all__ = [
    "CARDS",
    "CARDS_BY_ID",
    "Card",
    "Draw",
    "DrawnCard",
    "LANGUAGES",
    "POSITIONS",
    "POSITIONS_BY_ID",
    "Position",
    "SPREAD_NAME",
    "SPREAD_NOTE",
    "SUITS",
    "SUITS_BY_ID",
    "Suit",
    "Uncalled",
    "brief",
    "check_cards",
    "draw",
    "new_seed",
    "pick",
]

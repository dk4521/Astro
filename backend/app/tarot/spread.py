"""Drawing three cards, reproducibly.

**Why there is a seed.** Everything else this backend does is a pure function of
its input, and the app says so on the screen. A shuffle is the one thing here
that genuinely is random — so rather than hide that behind a server that
remembers, the randomness is pushed into a single value the caller gets back.
The seed *is* the draw: hand the same seed to `draw()` on any machine, in any
process, next year, and the same three cards come up the same way round. Nothing
is stored anywhere and the reading is still reproducible, which is the same
property a chart has.

It also closes a hole that would otherwise be real. `/v1/tarot/reading` costs a
credit, and it takes a seed rather than a list of cards: the server re-draws
from the seed and reads *that*. A client cannot pay for a reading of a hand it
made up.

**Why this spread and not past / present / future.** Three-card spreads are
usually sold as a timeline, and a timeline is a forecast — the one thing this
product does not do. Situation, obstacle, advice asks the same three questions
without claiming to know what happens next, and the third card lands on
something the reader can actually act on. That is the same choice the dasha
meanings make: name what the period asks of you, not how it turns out.

**The draw order is a contract.** The deck's order, `sample` before orientation,
and one coin per card — change any of those and every seed ever issued produces
different cards. `test_tarot.py` pins a known seed to a known hand for exactly
that reason.
"""

from __future__ import annotations

import hashlib
import random
import secrets
from dataclasses import dataclass

from .deck import CARDS, Card, Text

#: A card is as likely to come out reversed as upright, because a shuffled deck
#: really is a coin per card. Decks that use a lower rate are compensating for
#: reversals read as bad news; these reversals are written as another angle on
#: the same theme, so there is nothing to compensate for.
REVERSAL_CHANCE = 0.5


@dataclass(frozen=True, slots=True)
class Position:
    """One seat in the spread, and the question it asks."""

    id: str
    name: Text
    prompt: Text


POSITIONS: tuple[Position, ...] = (
    Position(
        id="situation",
        name={"en": "The situation", "hi": "स्थिति"},
        prompt={
            "en": "What is actually going on, as it stands.",
            "hi": "असल में क्या चल रहा है, जैसा है वैसा।",
        },
    ),
    Position(
        id="obstacle",
        name={"en": "The obstacle", "hi": "बाधा"},
        prompt={
            "en": "What is in the way — including the part of it that is yours.",
            "hi": "रास्ते में क्या है — वह हिस्सा भी जो आपका अपना है।",
        },
    ),
    Position(
        id="advice",
        name={"en": "The advice", "hi": "सलाह"},
        prompt={
            "en": "What you could actually do about it.",
            "hi": "इसके बारे में आप असल में क्या कर सकते हैं।",
        },
    ),
)

POSITIONS_BY_ID = {position.id: position for position in POSITIONS}

SPREAD_NAME: Text = {
    "en": "Situation · Obstacle · Advice",
    "hi": "स्थिति · बाधा · सलाह",
}

#: Shown under the spread, because the reader deserves to know what they are
#: not being sold. Same job as the caption under the Ashtakoot score.
SPREAD_NOTE: Text = {
    "en": (
        "Three cards, and none of them is the future. The shuffle is random and "
        "the seed below is the whole of it — the same seed always deals this "
        "exact hand. What the cards are for is thinking about the situation, "
        "not being told how it ends."
    ),
    "hi": (
        "तीन कार्ड, और इनमें से कोई भविष्य नहीं है। फेंटना सचमुच अनियमित है और नीचे "
        "दिया बीज ही उसका पूरा हिसाब है — वही बीज हमेशा यही तीन कार्ड निकालेगा। "
        "कार्ड इसलिए हैं कि स्थिति पर सोचा जा सके, यह जानने के लिए नहीं कि अंत क्या होगा।"
    ),
}


@dataclass(frozen=True, slots=True)
class DrawnCard:
    position: Position
    card: Card
    reversed: bool

    def meaning(self, language: str) -> str:
        """The written line for the way this card actually came up."""
        text = self.card.reversed if self.reversed else self.card.upright
        return text.get(language) or text["en"]


@dataclass(frozen=True, slots=True)
class Draw:
    seed: str
    cards: tuple[DrawnCard, ...]


def new_seed() -> str:
    """A fresh shuffle, as twelve hex characters.

    `secrets` rather than `random`: this is the only unpredictable thing in the
    product, and a seed drawn from a predictable generator would let a caller
    work out the next hand — which would make the shuffle a decoration.
    """
    return secrets.token_hex(6)


def _rng(seed: str) -> random.Random:
    """A generator derived from the seed, by arithmetic we own.

    `random.Random(some_string)` would also work today, but how CPython turns a
    string into state is an implementation detail — and this seed is a promise
    that the same value deals the same hand for as long as the product exists.
    Hashing it here means that promise depends on SHA-256 rather than on a
    future release of the interpreter.
    """
    digest = hashlib.sha256(seed.encode("utf-8")).digest()
    return random.Random(int.from_bytes(digest, "big"))


def draw(seed: str | None = None) -> Draw:
    """Deal the three cards for `seed`, or for a fresh one."""
    seed = seed or new_seed()
    rng = _rng(seed)

    # Sampled without replacement, because a deck cannot deal the same card
    # twice — and a spread with two of the same card would be a bug the reader
    # would notice long before we did.
    picked = rng.sample(CARDS, len(POSITIONS))

    return Draw(
        seed=seed,
        cards=tuple(
            DrawnCard(
                position=position,
                card=card,
                reversed=rng.random() < REVERSAL_CHANCE,
            )
            for position, card in zip(POSITIONS, picked)
        ),
    )


def brief(drawn: Draw, question: str | None, language: str) -> str:
    """The fact block handed to the model.

    The same discipline as the chart brief: everything the model is allowed to
    say about these cards is in here, written by a person, so a meaning it did
    not receive is a meaning it invented. The written line comes through in the
    reading's own language — a Hindi reading built from English source lines
    reads like a translation, because it is one.
    """
    lines = [
        "tarot draw",
        f"spread: {SPREAD_NAME['en']}",
        f"seed: {drawn.seed}",
        "",
    ]

    for index, item in enumerate(drawn.cards, start=1):
        orientation = "reversed" if item.reversed else "upright"
        name = item.card.name["en"]
        if language == "hi":
            name = f"{name} ({item.card.name['hi']})"

        lines += [
            f"{index}. {item.position.name['en']} — {item.position.prompt['en']}",
            f"   card: {name}, {orientation}",
            f"   written meaning: {item.meaning(language)}",
            "",
        ]

    asked = (question or "").strip()
    lines.append(f"their question: {asked}" if asked else "their question: none asked")

    return "\n".join(lines)

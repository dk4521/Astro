"""Checking a tarot reading against the cards that were actually dealt.

The chart side of this app has `ai/grounding.py`, which reads an interpretation
back and compares every placement claim against the computed chart. A tarot
reading has the same failure available to it in a smaller form: the model is
handed three cards and their written meanings, and the thing it can do wrong is
talk about a fourth.

So this checks one claim only — **that every card named was one of the three
dealt.** A finding means "this card was not in the spread", never "this is bad
tarot". Whether a reading is any good is not decidable here and is not tried.

**The check is deliberately narrow, in the same way and for the same reason.**
Half the major arcana are ordinary words: Death, Justice, Strength, The Sun, The
World, तारा, संसार, मृत्यु. A checker that flagged the sentence "an ending, not a
death" would produce false alarms, and a check that cries wolf gets switched
off — which costs more than the recall it bought. Two rules keep it quiet:

- English names are matched **case-sensitively**, so "The Sun" is a card and
  "the sun" is the sky.
- Names listed in `_SKIP_EN` / `_SKIP_HI` are not matched in that language at
  all, because capitalisation cannot save them. Devanagari has no case, so its
  list is the longer one.

Nothing is skipped in both languages by accident: a card dropped from English is
still checked in Hindi wherever its Hindi name is distinctive, and the tests
assert that every id in these lists is a real card.
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from .deck import CARDS, CARDS_BY_ID
from .spread import Draw

#: English names that are also ordinary English, even capitalised at the start
#: of a sentence — "Death is not the end", "Justice took a while".
_SKIP_EN = frozenset(
    {
        "major-death",
        "major-justice",
        "major-strength",
        "major-temperance",
        "major-judgement",
    }
)

#: The same list for Hindi, which is longer because Devanagari has no capital
#: letters to tell a card from a common noun. संसार, प्रेमी, तारा, सूर्य and
#: चंद्रमा all turn up in ordinary Hindi prose — and सूर्य and चंद्रमा turn up in
#: *this* app's other half, where they are grahas.
_SKIP_HI = _SKIP_EN | frozenset(
    {
        "major-fool",      # नादान — an everyday adjective
        "major-emperor",   # सम्राट
        "major-lovers",    # प्रेमी
        "major-chariot",   # रथ
        "major-star",      # तारा
        "major-moon",      # चंद्रमा
        "major-sun",       # सूर्य
        "major-world",     # संसार
    }
)


def _forms(language: str, skip: frozenset[str]) -> dict[str, str]:
    return {
        card.name[language]: card.id for card in CARDS if card.id not in skip
    }


_FORMS_EN = _forms("en", _SKIP_EN)
_FORMS_HI = _forms("hi", _SKIP_HI)


def _alternation(names: dict[str, str]) -> str:
    # Longest first, so "Ace of Wands" wins over any shorter name inside it.
    return "|".join(sorted(map(re.escape, names), key=len, reverse=True))


# `\b` does not work on Devanagari — matras, the anusvara and the virama are
# combining marks and not word characters, so a name ending in one has no word
# boundary after it at all. The same fix `ai/grounding.py` uses.
_MARKS = "ऀ-ःऺ-ॏ॑-ॗॢ-ॣ"
_EDGE_L = rf"(?<![\w{_MARKS}])"
_EDGE_R = rf"(?![\w{_MARKS}])"

# Case-sensitive on purpose: see the module docstring.
_CARD_EN = re.compile(rf"\b({_alternation(_FORMS_EN)})\b")
_CARD_HI = re.compile(rf"{_EDGE_L}({_alternation(_FORMS_HI)}){_EDGE_R}")


@dataclass(frozen=True, slots=True)
class Uncalled:
    """A card the reading named that the shuffle did not deal."""

    named: str      # the text as written
    card_id: str

    def __str__(self) -> str:
        return f"text names {self.named!r}, which was not in the spread"


def check(text: str, drawn: Draw) -> list[Uncalled]:
    """Cards named in `text` that are not in `drawn`.

    An empty list means nothing checkable was wrong, not that everything said
    was verified — the recall limits are in the module docstring.
    """
    dealt = {item.card.id for item in drawn.cards}

    found: list[Uncalled] = []
    seen: set[str] = set()

    for pattern, forms in ((_CARD_EN, _FORMS_EN), (_CARD_HI, _FORMS_HI)):
        for match in pattern.finditer(text):
            written = match.group(1)
            card_id = forms[written]
            if card_id in dealt or card_id in seen:
                continue
            seen.add(card_id)
            found.append(Uncalled(named=written, card_id=card_id))

    return found


# A stale id here would silently switch the check off for that card, so it is
# caught at import rather than by a reader wondering why nothing was flagged.
assert all(card_id in CARDS_BY_ID for card_id in _SKIP_HI), "unknown card id in a skip list"

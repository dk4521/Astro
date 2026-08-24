"""Turning three dealt cards into language.

The same shape as the chart's interpretation path, one layer up: deal
deterministically, render the result as facts written by a person, hand those
facts to the model, and check what comes back against what was dealt. The model
receives no card it was not given, so a fourth card in the reply is detectable
rather than merely discouraged.

Two checks run on the way out, and they answer different questions:

  `tarot.grounding` — did it name a card that was not in the spread?
  `ai.grounding.mentions_chart` — did it reach for astrology in a reply that
  was told there is no chart here?

The second one exists because of where this sits in the codebase. The system
prompt this shares with every other model call opens by declaring itself the
interpretation layer of a Vedic astrology app, and a long prompt is won by its
framing rather than by a rule in its middle. `tarot_directive` says there is no
chart; this measures whether that held.

**A reading that failed either check is never cached.** Same bet, same reason as
`ai/interpret.py`: storing an answer already known to be wrong turns one bad
reading into the same bad reading all day, and the retry the reader gets instead
is a request they were going to spend anyway.

The direction of the imports is deliberate — tarot depends on `ai`, and `ai`
knows nothing about tarot. The deck, the shuffle and the card check all work
with no key configured and nothing to spend.
"""

from __future__ import annotations

from ..ai import cache, grounding
from ..ai.client import Request, get_client
from ..ai.interpret import Interpretation
from ..ai.prompts import tarot_directive
from . import grounding as card_grounding
from .spread import Draw, brief


def _verify(text: str, drawn: Draw, language: str, cached: bool) -> Interpretation:
    contradictions = [str(finding) for finding in card_grounding.check(text, drawn)]
    contradictions += [
        f"astrology in a tarot reading: {term!r}"
        for term in grounding.mentions_chart(text)
    ]

    return Interpretation(
        text=text,
        language=language,
        model_grounded=not contradictions,
        contradictions=contradictions,
        cached=cached,
    )


def interpret(
    drawn: Draw,
    question: str | None = None,
    language: str = "hinglish",
) -> Interpretation:
    """Read the three cards, in the reader's language.

    Cached on the assembled request like every other model call here, which
    gives this one a useful property for free: the seed is in the brief, so the
    same spread and the same question come back instantly and — because the app
    keeps the answer on the device too — without a second credit.
    """
    request = Request(
        messages=[{"role": "user", "content": brief(drawn, question, language)}],
        suffix=tarot_directive(language),
    )

    stored = cache.get(request)
    if stored is not None:
        return _verify(stored, drawn, language, cached=True)

    result = _verify(get_client().complete(request), drawn, language, cached=False)
    if result.model_grounded:
        cache.put(request, result.text)
    return result

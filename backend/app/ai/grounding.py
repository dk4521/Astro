"""Checking interpretations against the chart they claim to describe.

app.md's central promise is that hallucinated positions are structurally
impossible. A prompt instruction alone does not make that true — it makes it
requested. This module makes it *checkable*: it reads the generated text back,
extracts every placement claim it can recognise, and compares each one against
the computed chart.

The check is deliberately narrow. It verifies claims of the form "<graha> is in
<rashi>" and "<graha> is in <nakshatra>" — the factual assertions that are both
unambiguous and the ones that matter, since a wrong rashi invalidates
everything said after it. It does not attempt to police interpretation, tone,
or claims it cannot decide, because a checker that guesses produces false
alarms and gets switched off.

A finding therefore means "this contradicts the chart", never "this is bad
astrology".
"""

from __future__ import annotations

import re
from dataclasses import dataclass

from ..astro import Chart
from ..astro import constants as K

# Both naming systems appear in output, so both are recognised. Mapped to the
# canonical Sanskrit name the engine uses.
_RASHI_ALIASES: dict[str, str] = {}
for _index, _sanskrit in enumerate(K.RASHIS):
    _RASHI_ALIASES[_sanskrit.lower()] = _sanskrit
    _RASHI_ALIASES[K.RASHIS_EN[_index].lower()] = _sanskrit

_GRAHA_ALIASES: dict[str, str] = {}
for _graha in K.GRAHAS:
    _GRAHA_ALIASES[_graha.lower()] = _graha
_GRAHA_ALIASES.update(
    {
        "surya": "Sun",
        "chandra": "Moon",
        "chandrama": "Moon",
        "mangal": "Mars",
        "mangala": "Mars",
        "kuja": "Mars",
        "budh": "Mercury",
        "budha": "Mercury",
        "guru": "Jupiter",
        "brihaspati": "Jupiter",
        "shukra": "Venus",
        "shukr": "Venus",
        "shani": "Saturn",
        "rahu": "Rahu",
        "ketu": "Ketu",
    }
)

_NAKSHATRA_ALIASES = {name.lower(): name for name in K.NAKSHATRAS}

# "Mars in Simha", "Mars is in Simha", "Mars sits in Simha", "Mangal Kanya mein".
# The connector is optional and bounded so the pattern cannot span sentences and
# pair a graha with a rashi mentioned somewhere else entirely.
_CONNECTOR = r"(?:\s+(?:is|sits|falls|lies|placed|positioned|located|in|your|the|hai|mein|me)){0,4}\s+"

_GRAHA_PATTERN = "|".join(sorted(map(re.escape, _GRAHA_ALIASES), key=len, reverse=True))
_RASHI_PATTERN = "|".join(sorted(map(re.escape, _RASHI_ALIASES), key=len, reverse=True))
_NAKSHATRA_PATTERN = "|".join(
    sorted(map(re.escape, _NAKSHATRA_ALIASES), key=len, reverse=True)
)

_RASHI_CLAIM = re.compile(
    rf"\b({_GRAHA_PATTERN}){_CONNECTOR}({_RASHI_PATTERN})\b",
    re.IGNORECASE,
)
_NAKSHATRA_CLAIM = re.compile(
    rf"\b({_GRAHA_PATTERN}){_CONNECTOR}({_NAKSHATRA_PATTERN})\b",
    re.IGNORECASE,
)
_HOUSE_CLAIM = re.compile(
    rf"\b({_GRAHA_PATTERN}){_CONNECTOR}(?:house\s+)?(\d{{1,2}})(?:st|nd|rd|th)?\s+house\b",
    re.IGNORECASE,
)


@dataclass(frozen=True, slots=True)
class Contradiction:
    """One statement in the output that the chart does not support."""

    claim: str          # the matched text
    graha: str
    asserted: str       # what the text said
    actual: str         # what the chart says
    kind: str           # "rashi" | "nakshatra" | "house"

    def __str__(self) -> str:
        return (
            f"{self.graha} {self.kind}: text says {self.asserted!r}, "
            f"chart says {self.actual!r}"
        )


def check(text: str, chart: Chart) -> list[Contradiction]:
    """Find statements in `text` that contradict `chart`.

    An empty list means nothing checkable was wrong — not that everything said
    was verified. The check has recall limits by design; see the module
    docstring.
    """
    found: list[Contradiction] = []

    for match in _RASHI_CLAIM.finditer(text):
        graha = _GRAHA_ALIASES[match.group(1).lower()]
        asserted = _RASHI_ALIASES[match.group(2).lower()]
        actual = chart.grahas[graha].placement.rashi
        if asserted != actual:
            found.append(
                Contradiction(
                    claim=match.group(0).strip(),
                    graha=graha,
                    asserted=asserted,
                    actual=actual,
                    kind="rashi",
                )
            )

    for match in _NAKSHATRA_CLAIM.finditer(text):
        graha = _GRAHA_ALIASES[match.group(1).lower()]
        asserted = _NAKSHATRA_ALIASES[match.group(2).lower()]
        actual = chart.grahas[graha].placement.nakshatra
        if asserted != actual:
            found.append(
                Contradiction(
                    claim=match.group(0).strip(),
                    graha=graha,
                    asserted=asserted,
                    actual=actual,
                    kind="nakshatra",
                )
            )

    for match in _HOUSE_CLAIM.finditer(text):
        graha = _GRAHA_ALIASES[match.group(1).lower()]
        asserted = int(match.group(2))
        if not 1 <= asserted <= 12:
            continue
        actual = chart.grahas[graha].house
        if asserted != actual:
            found.append(
                Contradiction(
                    claim=match.group(0).strip(),
                    graha=graha,
                    asserted=str(asserted),
                    actual=str(actual),
                    kind="house",
                )
            )

    return found

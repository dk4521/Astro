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

# All three naming systems appear in output, so all three are recognised, mapped
# to the canonical Sanskrit name the engine uses. Devanagari is not optional
# extra coverage: `hi` is a supported language and most of this market reads it,
# so without these a wrong placement in a Hindi reading was returned to the app
# with `grounded: true` — the check silently passing rather than running.
_RASHI_ALIASES: dict[str, str] = {}
for _index, _sanskrit in enumerate(K.RASHIS):
    _RASHI_ALIASES[_sanskrit.lower()] = _sanskrit
    _RASHI_ALIASES[K.RASHIS_EN[_index].lower()] = _sanskrit
    _RASHI_ALIASES[K.RASHIS_HI[_index]] = _sanskrit

_GRAHA_ALIASES: dict[str, str] = {}
for _graha in K.GRAHAS:
    _GRAHA_ALIASES[_graha.lower()] = _graha
    _GRAHA_ALIASES[K.GRAHA_HI[_graha]] = _graha
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
# Devanagari spellings a reading uses but `GRAHA_HI` does not emit.
_GRAHA_ALIASES.update(
    {
        "चंद्रमा": "Moon",
        "चन्द्र": "Moon",
        "चन्द्रमा": "Moon",
        "सूरज": "Sun",
        "बृहस्पति": "Jupiter",
        "शनी": "Saturn",
    }
)

_NAKSHATRA_ALIASES = {name.lower(): name for name in K.NAKSHATRAS}
_NAKSHATRA_ALIASES.update(dict(zip(K.NAKSHATRAS_HI, K.NAKSHATRAS)))

# Hindi writes house numbers as ordinal words far more often than as digits.
_HOUSE_ORDINALS_HI: dict[str, int] = {
    "पहले": 1, "पहला": 1, "प्रथम": 1,
    "दूसरे": 2, "दूसरा": 2, "द्वितीय": 2,
    "तीसरे": 3, "तीसरा": 3, "तृतीय": 3,
    "चौथे": 4, "चौथा": 4, "चतुर्थ": 4,
    "पांचवें": 5, "पाँचवें": 5, "पांचवे": 5, "पाँचवे": 5, "पंचम": 5,
    "छठे": 6, "छठा": 6, "छठवें": 6, "षष्ठ": 6,
    "सातवें": 7, "सातवे": 7, "सप्तम": 7,
    "आठवें": 8, "आठवे": 8, "अष्टम": 8,
    "नवें": 9, "नौवें": 9, "नौवे": 9, "नवम": 9,
    "दसवें": 10, "दसवे": 10, "दशम": 10,
    "ग्यारहवें": 11, "ग्यारहवे": 11, "एकादश": 11,
    "बारहवें": 12, "बारहवे": 12, "द्वादश": 12,
}

# `\b` cannot be used on Devanagari. Matras, the anusvara and the virama are
# combining marks, which Python does not count as word characters, so a name
# ending in one — कन्या, धनु, four of the twelve rashis — has no word boundary
# after it at all and `\bकन्या\b` never matches.
#
# `\w` already covers Devanagari letters and digits, so these edges add only the
# marks. Not the whole Devanagari block: the danda । that ends most Hindi
# sentences lives in it, and excluding it would break every claim written at the
# end of a sentence — which is where a claim usually is.
_MARKS = "ऀ-ःऺ-ॏ॑-ॗॢ-ॣ"
_EDGE_L = rf"(?<![\w{_MARKS}])"
_EDGE_R = rf"(?![\w{_MARKS}])"

# "Mars in Simha", "Mars is in Simha", "Mars sits in Simha", "Mangal Kanya mein",
# "चंद्रमा आपकी कुंडली में कर्क राशि में". The connector is optional and bounded so
# the pattern cannot span sentences and pair a graha with a rashi mentioned
# somewhere else entirely. No graha name is a connector, so a list — "चंद्र और
# मंगल मेष में" — pairs Mars with Mesha and leaves the Moon alone, as it should.
_CONNECTOR = (
    r"(?:\s+(?:is|sits|falls|lies|placed|positioned|located|in|your|the"
    r"|hai|mein|me"
    r"|में|है|हैं|स्थित|बैठा|बैठे|बैठी|आपका|आपकी|आपके|कुंडली|राशि|नक्षत्र"
    r"|का|की|के)){0,4}\s+"
)

_GRAHA_PATTERN = "|".join(sorted(map(re.escape, _GRAHA_ALIASES), key=len, reverse=True))
_RASHI_PATTERN = "|".join(sorted(map(re.escape, _RASHI_ALIASES), key=len, reverse=True))
_NAKSHATRA_PATTERN = "|".join(
    sorted(map(re.escape, _NAKSHATRA_ALIASES), key=len, reverse=True)
)
_ORDINAL_PATTERN = "|".join(
    sorted(map(re.escape, _HOUSE_ORDINALS_HI), key=len, reverse=True)
)

_RASHI_CLAIM = re.compile(
    rf"{_EDGE_L}({_GRAHA_PATTERN}){_CONNECTOR}({_RASHI_PATTERN}){_EDGE_R}",
    re.IGNORECASE,
)
_NAKSHATRA_CLAIM = re.compile(
    rf"{_EDGE_L}({_GRAHA_PATTERN}){_CONNECTOR}({_NAKSHATRA_PATTERN}){_EDGE_R}",
    re.IGNORECASE,
)
_HOUSE_CLAIM = re.compile(
    rf"{_EDGE_L}({_GRAHA_PATTERN}){_CONNECTOR}"
    rf"(?:house\s+)?(\d{{1,2}})(?:st|nd|rd|th)?\s+house\b",
    re.IGNORECASE,
)
# "शनि तीसरे भाव में", "मंगल 10वें घर में".
_HOUSE_CLAIM_HI = re.compile(
    rf"{_EDGE_L}(?P<graha>{_GRAHA_PATTERN}){_CONNECTOR}"
    rf"(?:(?P<word>{_ORDINAL_PATTERN})|(?P<digits>\d{{1,2}})\s*(?:वें|वे|वाँ|वां)?)"
    r"\s*(?:भाव|घर|स्थान)",
    re.IGNORECASE,
)

# Hindi states the location first at least as often as not — "छठे भाव में तुला
# राशि में बैठे गुरु" is ordinary phrasing, not an inversion. The patterns above
# are graha-first because English is, so Hindi needs its mirror or the checker
# reads only the half of a reading that happens to be worded like English. These
# are built from the Devanagari names alone, so they cannot fire on English or
# Hinglish text, where this ordering would be a genuinely different sentence.
_GRAHA_HI_PATTERN = "|".join(
    sorted(
        (re.escape(name) for name in _GRAHA_ALIASES if not name.isascii()),
        key=len,
        reverse=True,
    )
)
_RASHI_HI_PATTERN = "|".join(
    sorted(map(re.escape, K.RASHIS_HI), key=len, reverse=True)
)

_RASHI_CLAIM_HI_REVERSED = re.compile(
    rf"{_EDGE_L}({_RASHI_HI_PATTERN}){_CONNECTOR}({_GRAHA_HI_PATTERN}){_EDGE_R}",
)
_HOUSE_CLAIM_HI_REVERSED = re.compile(
    rf"{_EDGE_L}(?:(?P<word>{_ORDINAL_PATTERN})"
    rf"|(?P<digits>\d{{1,2}})\s*(?:वें|वे|वाँ|वां)?)"
    rf"\s*(?:भाव|घर|स्थान){_CONNECTOR}(?P<graha>{_GRAHA_HI_PATTERN}){_EDGE_R}",
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
        found += _rashi_finding(match.group(0), match.group(1), match.group(2), chart)

    for match in _RASHI_CLAIM_HI_REVERSED.finditer(text):
        # Same claim, stated the other way round: the rashi is group 1 here.
        found += _rashi_finding(match.group(0), match.group(2), match.group(1), chart)

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
        found += _house_finding(
            match.group(0), _GRAHA_ALIASES[match.group(1).lower()],
            int(match.group(2)), chart,
        )

    for pattern in (_HOUSE_CLAIM_HI, _HOUSE_CLAIM_HI_REVERSED):
        for match in pattern.finditer(text):
            word = match.group("word")
            asserted = _HOUSE_ORDINALS_HI[word] if word else int(match.group("digits"))
            found += _house_finding(
                match.group(0), _GRAHA_ALIASES[match.group("graha").lower()],
                asserted, chart,
            )

    # A reading that states the same wrong placement twice, or states it in a
    # form two patterns both recognise, is one contradiction and not two.
    unique: list[Contradiction] = []
    seen: set[tuple[str, str, str]] = set()
    for finding in found:
        key = (finding.graha, finding.kind, finding.asserted)
        if key not in seen:
            seen.add(key)
            unique.append(finding)

    return unique


def _rashi_finding(
    claim: str, graha_text: str, rashi_text: str, chart: Chart
) -> list[Contradiction]:
    """Compare one rashi claim, in whichever order it was written."""
    graha = _GRAHA_ALIASES[graha_text.lower()]
    asserted = _RASHI_ALIASES[rashi_text.lower()]
    actual = chart.grahas[graha].placement.rashi
    if asserted == actual:
        return []

    return [
        Contradiction(
            claim=claim.strip(),
            graha=graha,
            asserted=asserted,
            actual=actual,
            kind="rashi",
        )
    ]


def _house_finding(
    claim: str, graha: str, asserted: int, chart: Chart
) -> list[Contradiction]:
    """Compare one house claim, whichever script it was written in."""
    if not 1 <= asserted <= 12:
        return []

    actual = chart.grahas[graha].house
    if asserted == actual:
        return []

    return [
        Contradiction(
            claim=claim.strip(),
            graha=graha,
            asserted=str(asserted),
            actual=str(actual),
            kind="house",
        )
    ]

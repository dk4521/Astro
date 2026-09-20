"""Checking interpretations against the chart they claim to describe.

This module uses an LLM to extract factual placement claims from generated text,
and then deterministically validates them against the computed chart.

A finding means "this contradicts the chart", never "this is bad astrology".
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from enum import Enum

from pydantic import BaseModel, Field

from ..astro import Chart
from ..astro import constants as K
from .client import Request, get_client


class ClaimType(str, Enum):
    PLANET_RASHI = "planet_rashi"
    PLANET_NAKSHATRA = "planet_nakshatra"
    PLANET_HOUSE = "planet_house"

class StructuredClaim(BaseModel):
    claim_type: ClaimType = Field(description="The type of claim being made.")
    planet: str = Field(description="The planet (Graha) being discussed (e.g. Sun, Moon, Mars).")
    value: str = Field(description="The rashi name, nakshatra name, or house number (as a string, e.g. '7').")
    original_text: str = Field(description="The exact snippet of text making the claim.")

class ClaimList(BaseModel):
    claims: list[StructuredClaim]

class GroundingStatus(str, Enum):
    FACTUAL_PLACEMENT = "FACTUAL_PLACEMENT"
    TRADITIONAL_INTERPRETATION = "TRADITIONAL_INTERPRETATION"
    UNSUPPORTED_CLAIM = "UNSUPPORTED_CLAIM"
    CONTRADICTORY_CLAIM = "CONTRADICTORY_CLAIM"
    SAFETY_BLOCK = "SAFETY_BLOCK"

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

# Mapping from common planet names to canonical English ones
_GRAHA_ALIASES: dict[str, str] = {}
for _graha in K.GRAHAS:
    _GRAHA_ALIASES[_graha.lower()] = _graha
    _GRAHA_ALIASES[K.GRAHA_HI[_graha]] = _graha
_GRAHA_ALIASES.update({
    "surya": "Sun", "chandra": "Moon", "chandrama": "Moon",
    "mangal": "Mars", "mangala": "Mars", "kuja": "Mars",
    "budh": "Mercury", "budha": "Mercury",
    "guru": "Jupiter", "brihaspati": "Jupiter",
    "shukra": "Venus", "shukr": "Venus",
    "shani": "Saturn", "rahu": "Rahu", "ketu": "Ketu",
    "चंद्रमा": "Moon", "चन्द्र": "Moon", "चन्द्रमा": "Moon",
    "सूरज": "Sun", "बृहस्पति": "Jupiter", "शनी": "Saturn",
})

_RASHI_ALIASES: dict[str, str] = {}
for _index, _sanskrit in enumerate(K.RASHIS):
    _RASHI_ALIASES[_sanskrit.lower()] = _sanskrit
    _RASHI_ALIASES[K.RASHIS_EN[_index].lower()] = _sanskrit
    _RASHI_ALIASES[K.RASHIS_HI[_index]] = _sanskrit

_NAKSHATRA_ALIASES = {name.lower(): name for name in K.NAKSHATRAS}
_NAKSHATRA_ALIASES.update(dict(zip(K.NAKSHATRAS_HI, K.NAKSHATRAS)))


import functools


@functools.lru_cache(maxsize=256)
def extract_claims(text: str) -> list[StructuredClaim] | None:
    """Uses LLM to extract placement claims from text."""
    system_instruction = (
        "Extract all explicit astrological placement claims from the provided text. "
        "Only extract claims about a planet's Rashi (zodiac sign), Nakshatra, or House position. "
        "Do not extract interpretations, only factual placements like 'Jupiter is in Aries' or 'Mars in the 7th house'."
    )
    
    # We use a fast model for extraction to reduce latency
    request = Request(
        messages=[{"role": "user", "content": text}],
        suffix=system_instruction,
        max_tokens=2000,
        response_mime_type="application/json",
        response_schema=ClaimList
    )
    
    client = get_client()
    try:
        response_text = client.complete(request)
        data = json.loads(response_text)
        return ClaimList(**data).claims
    except Exception as e:
        print(f"Claim extraction failed: {e}")
        return None

def _normalize_planet(planet_str: str) -> str | None:
    return _GRAHA_ALIASES.get(planet_str.lower().strip())

def _normalize_rashi(rashi_str: str) -> str | None:
    return _RASHI_ALIASES.get(rashi_str.lower().strip())

def _normalize_nakshatra(nakshatra_str: str) -> str | None:
    return _NAKSHATRA_ALIASES.get(nakshatra_str.lower().strip())

def _normalize_house(house_str: str) -> int | None:
    # Handle digits
    try:
        return int("".join(filter(str.isdigit, house_str)))
    except ValueError:
        pass
    
    # Very basic fallback for Hindi ordinal words if LLM returns them directly
    house_words_hi = {
        "पहले": 1, "पहला": 1, "प्रथम": 1, "दूसरे": 2, "दूसरा": 2, "द्वितीय": 2,
        "तीसरे": 3, "तीसरा": 3, "तृतीय": 3, "चौथे": 4, "चौथा": 4, "चतुर्थ": 4,
        "पांचवें": 5, "पाँचवें": 5, "पंचम": 5, "छठे": 6, "छठा": 6, "षष्ठ": 6,
        "सातवें": 7, "सप्तम": 7, "आठवें": 8, "अष्टम": 8, "नवें": 9, "नौवें": 9, "नवम": 9,
        "दसवें": 10, "दशम": 10, "ग्यारहवें": 11, "एकादश": 11, "बारहवें": 12, "द्वादश": 12,
    }
    for word, num in house_words_hi.items():
        if word in house_str:
            return num
    return None

def check(text: str, chart: Chart) -> list[Contradiction]:
    """Find statements in `text` that contradict `chart`.
    Returns a list of Contradictions.
    """
    claims = extract_claims(text)
    found: list[Contradiction] = []
    
    for claim in claims:
        graha = _normalize_planet(claim.planet)
        if not graha:
            # If we don't recognize the planet, we skip checking it to avoid false positives
            continue
            
        chart_placement = chart.grahas[graha].placement
        chart_house = chart.grahas[graha].house
        
        if claim.claim_type == ClaimType.PLANET_RASHI:
            asserted = _normalize_rashi(claim.value)
            if asserted and asserted != chart_placement.rashi:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=asserted, actual=chart_placement.rashi, kind="rashi"
                ))
        elif claim.claim_type == ClaimType.PLANET_NAKSHATRA:
            asserted = _normalize_nakshatra(claim.value)
            if asserted and asserted != chart_placement.nakshatra:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=asserted, actual=chart_placement.nakshatra, kind="nakshatra"
                ))
        elif claim.claim_type == ClaimType.PLANET_HOUSE:
            asserted = _normalize_house(claim.value)
            if asserted is not None and asserted != chart_house:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=str(asserted), actual=str(chart_house), kind="house"
                ))
                
    # Deduplicate
    unique: list[Contradiction] = []
    seen: set[tuple[str, str, str]] = set()
    for finding in found:
        key = (finding.graha, finding.kind, finding.asserted)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
            
    return unique

def evaluate_status(claims: list[StructuredClaim], contradictions: list[Contradiction]) -> GroundingStatus:
    """Determine the categorical status of the generated text based on extracted claims and contradictions."""
    if contradictions:
        return GroundingStatus.CONTRADICTORY_CLAIM
    
    # Check if there are any claims to classify as FACTUAL_PLACEMENT vs TRADITIONAL_INTERPRETATION
    if claims:
        return GroundingStatus.FACTUAL_PLACEMENT
    return GroundingStatus.TRADITIONAL_INTERPRETATION

def check_and_evaluate(text: str, chart: Chart) -> tuple[list[Contradiction], GroundingStatus]:
    claims = extract_claims(text)
    if claims is None:
        return [], GroundingStatus.UNSUPPORTED_CLAIM
    
    found: list[Contradiction] = []
    for claim in claims:
        graha = _normalize_planet(claim.planet)
        if not graha:
            continue
            
        chart_placement = chart.grahas[graha].placement
        chart_house = chart.grahas[graha].house
        
        if claim.claim_type == ClaimType.PLANET_RASHI:
            asserted = _normalize_rashi(claim.value)
            if asserted and asserted != chart_placement.rashi:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=asserted, actual=chart_placement.rashi, kind="rashi"
                ))
        elif claim.claim_type == ClaimType.PLANET_NAKSHATRA:
            asserted = _normalize_nakshatra(claim.value)
            if asserted and asserted != chart_placement.nakshatra:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=asserted, actual=chart_placement.nakshatra, kind="nakshatra"
                ))
        elif claim.claim_type == ClaimType.PLANET_HOUSE:
            asserted = _normalize_house(claim.value)
            if asserted is not None and asserted != chart_house:
                found.append(Contradiction(
                    claim=claim.original_text, graha=graha,
                    asserted=str(asserted), actual=str(chart_house), kind="house"
                ))
                
    # Deduplicate
    unique: list[Contradiction] = []
    seen: set[tuple[str, str, str]] = set()
    for finding in found:
        key = (finding.graha, finding.kind, finding.asserted)
        if key not in seen:
            seen.add(key)
            unique.append(finding)
            
    status = evaluate_status(claims, unique)
    return unique, status


class SafetyCheckResult(BaseModel):
    is_crisis: bool = Field(description="True if the message indicates self-harm, hopelessness, or danger.")

def classify_safety(text: str) -> str:
    """Uses LLM to classify if the user message indicates a crisis."""
    system_instruction = (
        "You are a safety classifier for an astrology app. "
        "Your job is to determine if the user's message indicates a crisis, such as self-harm, "
        "suicidal ideation, hopelessness, or acute danger (e.g. domestic violence). "
        "If it is an ordinary question, return false."
    )
    request = Request(
        messages=[{"role": "user", "content": text}],
        suffix=system_instruction,
        max_tokens=500,
        response_mime_type="application/json",
        response_schema=SafetyCheckResult
    )
    client = get_client()
    try:
        response_text = client.complete(request)
        data = json.loads(response_text)
        return "CRISIS" if SafetyCheckResult(**data).is_crisis else "SAFE"
    except Exception as e:
        print(f"Safety classification failed: {e}")
        return "UNKNOWN"


# --- Tarot checking ---
_CHART_JARGON = (
    "kundali", "kundli", "janam kundali", "horoscope", "natal chart",
    "birth chart", "lagna", "ascendant", "nakshatra", "mahadasha",
    "antardasha", "pratyantardasha", "dasha", "vimshottari", "navamsa",
    "ayanamsa", "panchang",
    "कुंडली", "कुण्डली", "जन्मपत्री", "लग्न", "नक्षत्र", "महादशा",
    "अंतर्दशा", "प्रत्यंतर्दशा", "विंशोत्तरी", "नवांश", "अयनांश", "पंचांग", "ग्रह",
)

_CHART_BODIES = ("Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
                 "बुध", "बृहस्पति", "शुक्र", "शनि", "राहु", "केतु")

def mentions_chart(text: str) -> list[str]:
    """Astrology vocabulary in text that was told to contain none."""
    import re
    _MARKS = "ऀ-ःऺ-ॏ॑-ॗॢ-ॣ"
    _EDGE_L = rf"(?<![\w{_MARKS}])"
    _EDGE_R = rf"(?![\w{_MARKS}])"
    
    _JARGON_RE = re.compile(
        rf"{_EDGE_L}({'|'.join(sorted(map(re.escape, _CHART_JARGON), key=len, reverse=True))}){_EDGE_R}",
        re.IGNORECASE,
    )
    _BODY_RE = re.compile(
        rf"{_EDGE_L}({'|'.join(sorted(map(re.escape, _CHART_BODIES), key=len, reverse=True))}){_EDGE_R}"
    )
    
    found: list[str] = []
    seen: set[str] = set()

    for pattern in (_JARGON_RE, _BODY_RE):
        for match in pattern.finditer(text):
            term = match.group(1)
            folded = term.lower()
            if folded in seen:
                continue
            seen.add(folded)
            found.append(term)

    return found

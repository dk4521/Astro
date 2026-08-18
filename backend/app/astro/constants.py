"""Static Vedic astrology reference data.

Everything here is pure data — no computation, no I/O. These tables are the
vocabulary the rest of the engine speaks in.
"""

from __future__ import annotations

# --- Rashis (signs) ---------------------------------------------------------

RASHIS: tuple[str, ...] = (
    "Mesha", "Vrishabha", "Mithuna", "Karka", "Simha", "Kanya",
    "Tula", "Vrishchika", "Dhanu", "Makara", "Kumbha", "Meena",
)

RASHIS_EN: tuple[str, ...] = (
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
)

# Devanagari, for the same reason `GRAHA_HI` exists: a Hindi reading writes these
# names in script, and `grounding` cannot check a claim it cannot spell.
RASHIS_HI: tuple[str, ...] = (
    "मेष", "वृषभ", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुंभ", "मीन",
)

RASHI_LORDS: tuple[str, ...] = (
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter",
)

# chara = movable, sthira = fixed, dwiswabhava = dual
RASHI_MODALITY: tuple[str, ...] = (
    "chara", "sthira", "dwiswabhava", "chara", "sthira", "dwiswabhava",
    "chara", "sthira", "dwiswabhava", "chara", "sthira", "dwiswabhava",
)

RASHI_ELEMENT: tuple[str, ...] = (
    "fire", "earth", "air", "water", "fire", "earth",
    "air", "water", "fire", "earth", "air", "water",
)

# --- Nakshatras -------------------------------------------------------------

NAKSHATRAS: tuple[str, ...] = (
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni",
    "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha",
    "Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana",
    "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada",
    "Revati",
)

NAKSHATRAS_HI: tuple[str, ...] = (
    "अश्विनी", "भरणी", "कृत्तिका", "रोहिणी", "मृगशिरा", "आर्द्रा",
    "पुनर्वसु", "पुष्य", "आश्लेषा", "मघा", "पूर्वा फाल्गुनी",
    "उत्तरा फाल्गुनी", "हस्त", "चित्रा", "स्वाति", "विशाखा", "अनुराधा",
    "ज्येष्ठा", "मूल", "पूर्वाषाढ़ा", "उत्तराषाढ़ा", "श्रवण",
    "धनिष्ठा", "शतभिषा", "पूर्वा भाद्रपद", "उत्तरा भाद्रपद",
    "रेवती",
)

# Vimshottari lord of each nakshatra, repeating every 9 starting at Ashwini.
NAKSHATRA_LORDS: tuple[str, ...] = tuple(
    ("Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury")[i % 9]
    for i in range(27)
)

NAKSHATRA_ARC = 360.0 / 27.0        # 13°20'
PADA_ARC = NAKSHATRA_ARC / 4.0      # 3°20'
RASHI_ARC = 30.0
NAVAMSA_ARC = RASHI_ARC / 9.0       # 3°20'

# --- Grahas (planets) -------------------------------------------------------

# Order matters: this is the order charts are rendered in.
GRAHAS: tuple[str, ...] = (
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu",
)

GRAHA_HI: dict[str, str] = {
    "Sun": "सूर्य",
    "Moon": "चंद्र",
    "Mars": "मंगल",
    "Mercury": "बुध",
    "Jupiter": "गुरु",
    "Venus": "शुक्र",
    "Saturn": "शनि",
    "Rahu": "राहु",
    "Ketu": "केतु",
    "Ascendant": "लग्न",
}

# Rahu and Ketu are always retrograde in the mean-node model; they get special
# handling in the engine rather than a speed lookup.
SHADOW_GRAHAS: frozenset[str] = frozenset({"Rahu", "Ketu"})

# --- Vimshottari dasha ------------------------------------------------------

VIMSHOTTARI_ORDER: tuple[str, ...] = (
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
)

VIMSHOTTARI_YEARS: dict[str, float] = {
    "Ketu": 7.0,
    "Venus": 20.0,
    "Sun": 6.0,
    "Moon": 10.0,
    "Mars": 7.0,
    "Rahu": 18.0,
    "Jupiter": 16.0,
    "Saturn": 19.0,
    "Mercury": 17.0,
}

VIMSHOTTARI_TOTAL_YEARS = 120.0

# The Vimshottari cycle is defined against a 360-day "savana" year convention in
# some texts, but the mainstream modern implementation (and every ephemeris we
# would be checked against) uses the Julian year of 365.25 days.
DAYS_PER_YEAR = 365.25

# --- Panchang ---------------------------------------------------------------

TITHI_NAMES: tuple[str, ...] = (
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami", "Shashthi",
    "Saptami", "Ashtami", "Navami", "Dashami", "Ekadashi", "Dwadashi",
    "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
)

YOGA_NAMES: tuple[str, ...] = (
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana", "Atiganda",
    "Sukarma", "Dhriti", "Shula", "Ganda", "Vriddhi", "Dhruva", "Vyaghata",
    "Harshana", "Vajra", "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma", "Indra", "Vaidhriti",
)

VARA_NAMES: tuple[str, ...] = (
    "Ravivara", "Somavara", "Mangalavara", "Budhavara",
    "Guruvara", "Shukravara", "Shanivara",
)

VARA_LORDS: tuple[str, ...] = (
    "Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn",
)

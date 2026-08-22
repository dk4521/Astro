"""Ashtakoot Milan — the eight-fold marriage matching, computed honestly.

**What this module does and does not claim.**

It computes. Every koot below is ordinary arithmetic over two janma nakshatras
and their rashis, and this file exists so a reader can check the number rather
than be handed it. That is the whole reason it belongs in a product like this
one: the procedure is used against people, and it is used most easily against
people who cannot do the arithmetic themselves.

It does not grade. Nothing here returns a verdict, a threshold, a colour, or a
word like "compatible" — because a score out of 36 is not a fact about two
people, and the app says so in chapter 30. The caller gets eight numbers and
the reasons for them.

**Conventions, because they vary.** Ashtakoot is not one procedure but a family
of them, and two panchangs will disagree about a point or two. Where sources
differ this module follows the most widely implemented reading and says so at
the table concerned. The places that actually vary are Vashya, the Tara point
scheme, and the Yoni matrix; the other five are stable across sources.
"""

from __future__ import annotations

from dataclasses import dataclass

from . import constants as K

# --- 1. Varna (1 point) -----------------------------------------------------
#
# From the rashi's element: water is Brahmin, fire Kshatriya, air Vaishya, earth
# Shudra. The point is scored when the groom's varna is not below the bride's —
# the one koot in the set that is openly asymmetric, and worth seeing plainly
# rather than buried.

VARNA_BY_ELEMENT = {"water": 4, "fire": 3, "air": 2, "earth": 1}
VARNA_NAMES = {4: "Brahmin", 3: "Kshatriya", 2: "Vaishya", 1: "Shudra"}
VARNA_NAMES_HI = {4: "ब्राह्मण", 3: "क्षत्रिय", 2: "वैश्य", 1: "शूद्र"}


def _varna_rank(rashi_index: int) -> int:
    return VARNA_BY_ELEMENT[K.RASHI_ELEMENT[rashi_index]]


# --- 2. Vashya (2 points) ---------------------------------------------------
#
# Five classes. Sources differ on the split halves of Dhanu and Makara; this
# follows the common simplification of treating each rashi as one class.

VASHYA_BY_RASHI = (
    "chatushpada",  # Mesha
    "chatushpada",  # Vrishabha
    "manava",       # Mithuna
    "jalachara",    # Karka
    "vanachara",    # Simha
    "manava",       # Kanya
    "manava",       # Tula
    "keeta",        # Vrishchika
    "chatushpada",  # Dhanu
    "jalachara",    # Makara
    "manava",       # Kumbha
    "jalachara",    # Meena
)

VASHYA_NAMES = {
    "chatushpada": "Chatushpada",
    "manava": "Manava",
    "jalachara": "Jalachara",
    "vanachara": "Vanachara",
    "keeta": "Keeta",
}
VASHYA_NAMES_HI = {
    "chatushpada": "चतुष्पद",
    "manava": "मानव",
    "jalachara": "जलचर",
    "vanachara": "वनचर",
    "keeta": "कीट",
}

# Rows are the bride's class, columns the groom's. 2 for the same class, 1 for a
# workable pairing, 0.5 where one class is said to be controlled by the other,
# 0 for the pairs the texts set against each other.
_VASHYA_SCORES: dict[tuple[str, str], float] = {}


def _vashya_table() -> dict[tuple[str, str], float]:
    if _VASHYA_SCORES:
        return _VASHYA_SCORES

    classes = ("chatushpada", "manava", "jalachara", "vanachara", "keeta")
    for a in classes:
        for b in classes:
            _VASHYA_SCORES[(a, b)] = 2.0 if a == b else 1.0

    # The pairings the texts single out.
    for pair, score in {
        ("chatushpada", "vanachara"): 0.0,
        ("vanachara", "chatushpada"): 0.0,
        ("manava", "vanachara"): 0.5,
        ("vanachara", "manava"): 0.5,
        ("jalachara", "chatushpada"): 0.5,
        ("chatushpada", "jalachara"): 0.5,
        ("keeta", "jalachara"): 0.5,
        ("jalachara", "keeta"): 0.5,
    }.items():
        _VASHYA_SCORES[pair] = score

    return _VASHYA_SCORES


# --- 3. Tara (3 points) -----------------------------------------------------
#
# Count from one janma nakshatra to the other and take the remainder mod 9. The
# 3rd, 5th and 7th taras are the inauspicious ones. Counted both ways: each
# direction is worth half, so a pair can score 3, 1.5 or 0.

_INAUSPICIOUS_TARA = frozenset({3, 5, 7})


def _tara_ok(from_index: int, to_index: int) -> bool:
    count = ((to_index - from_index) % 27) + 1
    return (count % 9) not in _INAUSPICIOUS_TARA


# --- 4. Yoni (4 points) -----------------------------------------------------
#
# Each nakshatra carries an animal. Same animal scores full; the seven classical
# enemy pairs score nothing; everything else sits between.
#
# The full 14x14 matrix differs noticeably between sources — more than any other
# koot here — so this module implements the part every source agrees on (the
# identical case and the seven enmities) and treats the rest as neutral rather
# than inventing a gradation it cannot stand behind.

NAKSHATRA_YONI = (
    "horse", "elephant", "sheep", "serpent", "serpent", "dog", "cat", "sheep",
    "cat", "rat", "rat", "cow", "buffalo", "tiger", "buffalo", "tiger", "deer",
    "deer", "dog", "monkey", "mongoose", "monkey", "lion", "horse", "lion",
    "cow", "elephant",
)

YONI_NAMES = {
    "horse": "Horse", "elephant": "Elephant", "sheep": "Sheep", "serpent": "Serpent",
    "dog": "Dog", "cat": "Cat", "rat": "Rat", "cow": "Cow", "buffalo": "Buffalo",
    "tiger": "Tiger", "deer": "Deer", "monkey": "Monkey", "mongoose": "Mongoose",
    "lion": "Lion",
}
YONI_NAMES_HI = {
    "horse": "अश्व", "elephant": "गज", "sheep": "मेष", "serpent": "सर्प",
    "dog": "श्वान", "cat": "मार्जार", "rat": "मूषक", "cow": "गौ", "buffalo": "महिष",
    "tiger": "व्याघ्र", "deer": "मृग", "monkey": "वानर", "mongoose": "नकुल",
    "lion": "सिंह",
}

#: The pairs the texts set against each other. Symmetric by construction below.
YONI_ENMITIES = (
    ("cow", "tiger"),
    ("elephant", "lion"),
    ("horse", "buffalo"),
    ("dog", "deer"),
    ("monkey", "sheep"),
    ("cat", "rat"),
    ("serpent", "mongoose"),
)

_ENEMY_PAIRS = frozenset(
    frozenset(pair) for pair in YONI_ENMITIES
)


# --- 5. Graha Maitri (5 points) ---------------------------------------------
#
# Friendship between the lords of the two Moon signs, by the classical natural
# relationships. Points: 5 mutual friends, 4 friend-neutral, 3 neutral-neutral,
# 1 friend-enemy, 0.5 neutral-enemy, 0 mutual enemies.

GRAHA_FRIENDS: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Moon", "Mars", "Jupiter"}),
    "Moon": frozenset({"Sun", "Mercury"}),
    "Mars": frozenset({"Sun", "Moon", "Jupiter"}),
    "Mercury": frozenset({"Sun", "Venus"}),
    "Jupiter": frozenset({"Sun", "Moon", "Mars"}),
    "Venus": frozenset({"Mercury", "Saturn"}),
    "Saturn": frozenset({"Mercury", "Venus"}),
}

GRAHA_ENEMIES: dict[str, frozenset[str]] = {
    "Sun": frozenset({"Venus", "Saturn"}),
    "Moon": frozenset(),
    "Mars": frozenset({"Mercury"}),
    "Mercury": frozenset({"Moon"}),
    "Jupiter": frozenset({"Mercury", "Venus"}),
    "Venus": frozenset({"Sun", "Moon"}),
    "Saturn": frozenset({"Sun", "Moon", "Mars"}),
}


def _relation(a: str, b: str) -> str:
    if a == b:
        return "friend"
    if b in GRAHA_FRIENDS.get(a, frozenset()):
        return "friend"
    if b in GRAHA_ENEMIES.get(a, frozenset()):
        return "enemy"
    return "neutral"


_MAITRI_SCORES = {
    ("friend", "friend"): 5.0,
    ("friend", "neutral"): 4.0,
    ("neutral", "friend"): 4.0,
    ("neutral", "neutral"): 3.0,
    ("friend", "enemy"): 1.0,
    ("enemy", "friend"): 1.0,
    ("neutral", "enemy"): 0.5,
    ("enemy", "neutral"): 0.5,
    ("enemy", "enemy"): 0.0,
}


# --- 6. Gana (6 points) -----------------------------------------------------

NAKSHATRA_GANA = (
    "deva", "manushya", "rakshasa", "manushya", "deva", "manushya", "deva",
    "deva", "rakshasa", "rakshasa", "manushya", "manushya", "deva", "rakshasa",
    "deva", "rakshasa", "deva", "rakshasa", "rakshasa", "manushya", "manushya",
    "deva", "rakshasa", "rakshasa", "manushya", "manushya", "deva",
)

GANA_NAMES = {"deva": "Deva", "manushya": "Manushya", "rakshasa": "Rakshasa"}
GANA_NAMES_HI = {"deva": "देव", "manushya": "मनुष्य", "rakshasa": "राक्षस"}

# Rows the bride's gana, columns the groom's — asymmetric, and again worth
# seeing rather than smoothing over.
_GANA_SCORES = {
    ("deva", "deva"): 6.0,
    ("deva", "manushya"): 5.0,
    ("deva", "rakshasa"): 0.0,
    ("manushya", "deva"): 6.0,
    ("manushya", "manushya"): 6.0,
    ("manushya", "rakshasa"): 0.0,
    ("rakshasa", "deva"): 1.0,
    ("rakshasa", "manushya"): 0.0,
    ("rakshasa", "rakshasa"): 6.0,
}


# --- 7. Bhakoot (7 points) --------------------------------------------------
#
# The distance between the two Moon signs, counted both ways. The 6-8, 9-5 and
# 2-12 relationships score nothing; every other distance scores full.

_BHAKOOT_ZERO = frozenset({(2, 12), (12, 2), (5, 9), (9, 5), (6, 8), (8, 6)})


# --- 8. Nadi (8 points) -----------------------------------------------------
#
# Three nadis, nine nakshatras each. The same nadi on both sides scores nothing;
# anything else scores full. This is the single heaviest koot, and the one most
# often used on its own to refuse a match.

NAKSHATRA_NADI = (
    "adi", "madhya", "antya", "antya", "madhya", "adi", "adi", "madhya",
    "antya", "antya", "madhya", "adi", "adi", "madhya", "antya", "antya",
    "madhya", "adi", "adi", "madhya", "antya", "antya", "madhya", "adi",
    "adi", "madhya", "antya",
)


NADI_NAMES = {"adi": "Adi", "madhya": "Madhya", "antya": "Antya"}
NADI_NAMES_HI = {"adi": "आदि", "madhya": "मध्य", "antya": "अंत्य"}


# --- The result -------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class Koot:
    """One of the eight, with the values it was computed from."""

    name: str
    points: float
    maximum: float
    #: What each side contributed — the two labels the score came from, in both
    #: scripts. Devanagari beside Latin everywhere, as the rest of the API does:
    #: a Hindi reader looking at a table of koot names in Devanagari should not
    #: find the values that produced them in Latin.
    bride: str
    bride_hi: str
    groom: str
    groom_hi: str


@dataclass(frozen=True, slots=True)
class Ashtakoot:
    koots: tuple[Koot, ...]

    @property
    def total(self) -> float:
        return sum(k.points for k in self.koots)

    @property
    def maximum(self) -> float:
        return sum(k.maximum for k in self.koots)


def ashtakoot(
    bride_nakshatra: int,
    bride_rashi: int,
    groom_nakshatra: int,
    groom_rashi: int,
) -> Ashtakoot:
    """The eight koots for two janma nakshatras and their Moon signs.

    Indices, not names, because the caller already has them from `decompose`
    and a name would only be a second thing to keep in step.

    The bride/groom split is the tradition's own and is not symmetric — Varna
    and Gana in particular score differently if the two are swapped. Naming the
    roles is more honest than pretending the procedure treats them alike.
    """
    bride_lord = K.RASHI_LORDS[bride_rashi]
    groom_lord = K.RASHI_LORDS[groom_rashi]

    # 1. Varna
    bride_varna, groom_varna = _varna_rank(bride_rashi), _varna_rank(groom_rashi)
    varna = Koot(
        "varna",
        1.0 if groom_varna >= bride_varna else 0.0,
        1.0,
        VARNA_NAMES[bride_varna],
        VARNA_NAMES_HI[bride_varna],
        VARNA_NAMES[groom_varna],
        VARNA_NAMES_HI[groom_varna],
    )

    # 2. Vashya
    bride_vashya = VASHYA_BY_RASHI[bride_rashi]
    groom_vashya = VASHYA_BY_RASHI[groom_rashi]
    vashya = Koot(
        "vashya",
        _vashya_table()[(bride_vashya, groom_vashya)],
        2.0,
        VASHYA_NAMES[bride_vashya],
        VASHYA_NAMES_HI[bride_vashya],
        VASHYA_NAMES[groom_vashya],
        VASHYA_NAMES_HI[groom_vashya],
    )

    # 3. Tara
    forward = _tara_ok(bride_nakshatra, groom_nakshatra)
    backward = _tara_ok(groom_nakshatra, bride_nakshatra)
    tara = Koot(
        "tara",
        (1.5 if forward else 0.0) + (1.5 if backward else 0.0),
        3.0,
        K.NAKSHATRAS[bride_nakshatra],
        K.NAKSHATRAS_HI[bride_nakshatra],
        K.NAKSHATRAS[groom_nakshatra],
        K.NAKSHATRAS_HI[groom_nakshatra],
    )

    # 4. Yoni
    bride_yoni = NAKSHATRA_YONI[bride_nakshatra]
    groom_yoni = NAKSHATRA_YONI[groom_nakshatra]
    if bride_yoni == groom_yoni:
        yoni_points = 4.0
    elif frozenset({bride_yoni, groom_yoni}) in _ENEMY_PAIRS:
        yoni_points = 0.0
    else:
        yoni_points = 2.0
    yoni = Koot(
        "yoni",
        yoni_points,
        4.0,
        YONI_NAMES[bride_yoni],
        YONI_NAMES_HI[bride_yoni],
        YONI_NAMES[groom_yoni],
        YONI_NAMES_HI[groom_yoni],
    )

    # 5. Graha Maitri
    maitri = Koot(
        "graha_maitri",
        _MAITRI_SCORES[
            (_relation(bride_lord, groom_lord), _relation(groom_lord, bride_lord))
        ],
        5.0,
        bride_lord,
        K.GRAHA_HI[bride_lord],
        groom_lord,
        K.GRAHA_HI[groom_lord],
    )

    # 6. Gana
    bride_gana = NAKSHATRA_GANA[bride_nakshatra]
    groom_gana = NAKSHATRA_GANA[groom_nakshatra]
    gana = Koot(
        "gana",
        _GANA_SCORES[(bride_gana, groom_gana)],
        6.0,
        GANA_NAMES[bride_gana],
        GANA_NAMES_HI[bride_gana],
        GANA_NAMES[groom_gana],
        GANA_NAMES_HI[groom_gana],
    )

    # 7. Bhakoot
    forward_distance = ((groom_rashi - bride_rashi) % 12) + 1
    backward_distance = ((bride_rashi - groom_rashi) % 12) + 1
    bhakoot = Koot(
        "bhakoot",
        0.0 if (forward_distance, backward_distance) in _BHAKOOT_ZERO else 7.0,
        7.0,
        K.RASHIS[bride_rashi],
        K.RASHIS_HI[bride_rashi],
        K.RASHIS[groom_rashi],
        K.RASHIS_HI[groom_rashi],
    )

    # 8. Nadi
    bride_nadi = NAKSHATRA_NADI[bride_nakshatra]
    groom_nadi = NAKSHATRA_NADI[groom_nakshatra]
    nadi = Koot(
        "nadi",
        0.0 if bride_nadi == groom_nadi else 8.0,
        8.0,
        NADI_NAMES[bride_nadi],
        NADI_NAMES_HI[bride_nadi],
        NADI_NAMES[groom_nadi],
        NADI_NAMES_HI[groom_nadi],
    )

    return Ashtakoot((varna, vashya, tara, yoni, maitri, gana, bhakoot, nadi))

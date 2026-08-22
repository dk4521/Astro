"""Tests for Ashtakoot Milan.

The procedure is used against people — most often against women, as chapter 30
says — so the arithmetic being checkable is the point of shipping it at all.
These tests are what make it checkable by something other than eye.
"""

from __future__ import annotations

from collections import Counter

import pytest

from app.astro import constants as K
from app.astro.matching import (
    NAKSHATRA_GANA,
    NAKSHATRA_NADI,
    NAKSHATRA_YONI,
    VASHYA_BY_RASHI,
    YONI_ENMITIES,
    ashtakoot,
)

# Pushya (7) in Karka (3), and Mula (18) in Dhanu (8).
PUSHYA_KARKA = (7, 3)
MULA_DHANU = (18, 8)


# --- The tables -------------------------------------------------------------


def test_every_nakshatra_has_every_attribute():
    for table in (NAKSHATRA_YONI, NAKSHATRA_GANA, NAKSHATRA_NADI):
        assert len(table) == len(K.NAKSHATRAS) == 27
        assert all(value for value in table)
    assert len(VASHYA_BY_RASHI) == len(K.RASHIS) == 12


def test_gana_and_nadi_split_the_nakshatras_evenly():
    """Nine each is a structural property of both schemes, and a typo in a
    27-entry table is exactly the error nobody spots by reading."""
    assert set(Counter(NAKSHATRA_GANA).values()) == {9}
    assert set(Counter(NAKSHATRA_NADI).values()) == {9}


def test_the_yoni_table_uses_fourteen_animals():
    assert len(set(NAKSHATRA_YONI)) == 14


def test_every_enmity_names_animals_that_exist():
    animals = set(NAKSHATRA_YONI)
    for a, b in YONI_ENMITIES:
        assert a in animals and b in animals, (a, b)
        assert a != b


# --- The total --------------------------------------------------------------


def test_the_maximum_is_thirty_six():
    result = ashtakoot(*PUSHYA_KARKA, *MULA_DHANU)
    assert result.maximum == 36.0
    assert [k.maximum for k in result.koots] == [1, 2, 3, 4, 5, 6, 7, 8]


def test_a_score_never_leaves_its_range():
    """Every pairing of all 27 nakshatras against all 12 rashis, both roles."""
    for bride_n in range(27):
        for groom_n in range(27):
            result = ashtakoot(bride_n, bride_n % 12, groom_n, groom_n % 12)
            assert 0.0 <= result.total <= 36.0
            for koot in result.koots:
                assert 0.0 <= koot.points <= koot.maximum, koot


# --- Individual koots, checkable by hand ------------------------------------


def test_the_same_nakshatra_scores_nothing_for_nadi():
    """The heaviest koot, and the one most often used alone to refuse a match:
    identical janma nakshatras share a nadi and score zero out of eight."""
    result = ashtakoot(7, 3, 7, 3)
    nadi = next(k for k in result.koots if k.name == "nadi")
    assert nadi.points == 0.0
    # And the total is capped well below the maximum by that alone.
    assert result.total == 28.0


def test_bhakoot_is_zero_for_the_six_eight_relationship():
    karka_dhanu = ashtakoot(7, 3, 18, 8)
    bhakoot = next(k for k in karka_dhanu.koots if k.name == "bhakoot")
    assert bhakoot.points == 0.0


@pytest.mark.parametrize(
    "bride_rashi, groom_rashi, expected",
    [
        (0, 0, 7.0),    # same sign
        (0, 1, 0.0),    # 2-12
        (0, 4, 0.0),    # 5-9
        (0, 5, 0.0),    # 6-8
        (0, 3, 7.0),    # 4-10, unremarked
    ],
)
def test_bhakoot_follows_the_three_forbidden_distances(bride_rashi, groom_rashi, expected):
    result = ashtakoot(0, bride_rashi, 0, groom_rashi)
    assert next(k for k in result.koots if k.name == "bhakoot").points == expected


def test_graha_maitri_reads_the_relationship_from_each_side():
    """Moon sees Jupiter as neutral; Jupiter sees Moon as a friend. One-sided
    friendship scores 4, not 5 — the asymmetry is the whole point of the koot."""
    result = ashtakoot(7, 3, 18, 8)  # Karka (Moon) x Dhanu (Jupiter)
    maitri = next(k for k in result.koots if k.name == "graha_maitri")
    assert maitri.points == 4.0
    assert (maitri.bride, maitri.groom) == ("Moon", "Jupiter")


def test_the_same_yoni_scores_full_and_an_enemy_pair_scores_nothing():
    # Rohini (3) and Mrigashira (4) are both serpent.
    same = ashtakoot(3, 1, 4, 1)
    assert next(k for k in same.koots if k.name == "yoni").points == 4.0

    # Uttara Phalguni (11) is cow, Chitra (13) is tiger — a named enmity.
    enemies = ashtakoot(11, 5, 13, 5)
    assert next(k for k in enemies.koots if k.name == "yoni").points == 0.0


def test_varna_and_gana_are_not_symmetric():
    """Swapping the two people changes the score, because the procedure itself
    is asymmetric. Hiding that would make it look fairer than it is."""
    forward = ashtakoot(9, 4, 7, 3)   # Magha/Simha  x  Pushya/Karka
    reversed_ = ashtakoot(7, 3, 9, 4)
    assert forward.total != reversed_.total


def test_tara_counts_in_both_directions():
    result = ashtakoot(0, 0, 2, 0)  # Ashwini x Krittika: 3rd tara one way
    tara = next(k for k in result.koots if k.name == "tara")
    assert tara.points in (0.0, 1.5, 3.0)

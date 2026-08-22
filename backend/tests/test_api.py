"""Tests for the HTTP surface."""

from __future__ import annotations

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.astro import EPHEMERIS_MODE
from app.main import app

client = TestClient(app)

BIRTH = {
    "date": "1947-08-15",
    "time": "00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "place": "New Delhi, India",
}


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    body = response.json()
    assert body["status"] == "ok"
    # Names the kernel that produced the numbers, so results stay auditable.
    assert body["ephemeris_mode"] == EPHEMERIS_MODE
    assert body["ephemeris_mode"]


def test_chart_endpoint():
    response = client.post("/v1/chart", json=BIRTH)
    assert response.status_code == 200
    body = response.json()

    assert body["lagna"]["rashi"] == "Vrishabha"
    assert body["moon_rashi"] == "Karka"
    assert body["janma_nakshatra"] == "Pushya"
    assert len(body["grahas"]) == 9
    assert len(body["houses"]) == 12
    assert body["meta"]["timezone"] == "Asia/Kolkata"
    assert body["meta"]["place"] == "New Delhi, India"


def test_chart_meta_reports_provenance():
    """A chart must say what produced it, so results stay auditable."""
    body = client.post("/v1/chart", json=BIRTH).json()
    meta = body["meta"]
    assert meta["ayanamsa_name"] == "Lahiri (Chitrapaksha)"
    assert meta["house_system"] == "whole-sign"
    assert meta["ephemeris_mode"] == EPHEMERIS_MODE
    assert meta["julian_day"] > 0


def test_panchang_endpoint():
    body = client.post("/v1/panchang", json=BIRTH).json()
    assert body["paksha"] == "Krishna"
    assert body["tithi"] == "Trayodashi"
    assert body["vara"] == "Guruvara"


def test_dasha_endpoint_defaults_to_now():
    response = client.post("/v1/dasha", json=BIRTH)
    assert response.status_code == 200
    body = response.json()

    assert body["janma_nakshatra_lord"] == "Saturn"
    assert body["balance_years"] == pytest.approx(18.07, abs=0.05)
    assert len(body["periods"]) == 9
    # Default depth is 2, so mahadashas carry antardashas but not deeper.
    assert len(body["periods"][0]["children"]) == 9
    assert body["periods"][0]["children"][0]["children"] == []


def test_dasha_active_periods_at_a_given_moment():
    response = client.post(
        "/v1/dasha",
        json=BIRTH,
        params={"as_of": "1990-01-01T00:00:00Z", "levels": 3},
    )
    body = response.json()

    assert len(body["active"]) == 3
    assert [p["level"] for p in body["active"]] == [1, 2, 3]

    moment = dt.datetime(1990, 1, 1, tzinfo=dt.timezone.utc)
    for period in body["active"]:
        start = dt.datetime.fromisoformat(period["start"])
        end = dt.datetime.fromisoformat(period["end"])
        assert start <= moment < end


def test_dasha_levels_are_bounded():
    assert client.post("/v1/dasha", json=BIRTH, params={"levels": 0}).status_code == 422
    assert client.post("/v1/dasha", json=BIRTH, params={"levels": 4}).status_code == 422


def test_reading_endpoint_bundles_everything():
    body = client.post("/v1/reading", json=BIRTH).json()
    assert set(body) == {"chart", "panchang", "dasha"}
    assert body["chart"]["lagna"]["rashi"] == "Vrishabha"
    assert body["panchang"]["nakshatra"] == "Pushya"
    assert body["dasha"]["janma_nakshatra_lord"] == "Saturn"


def test_rejects_invalid_coordinates():
    bad = BIRTH | {"latitude": 120.0}
    assert client.post("/v1/chart", json=bad).status_code == 422


def test_rejects_unknown_timezone():
    bad = BIRTH | {"timezone": "Mars/Olympus_Mons"}
    assert client.post("/v1/chart", json=bad).status_code == 422


def test_timezone_override_is_honoured():
    body = client.post("/v1/chart", json=BIRTH | {"timezone": "UTC"}).json()
    assert body["meta"]["timezone"] == "UTC"
    assert body["meta"]["birth_utc"].startswith("1947-08-15T00:00")


def test_missing_required_fields():
    assert client.post("/v1/chart", json={"date": "1990-01-01"}).status_code == 422


def test_place_search():
    body = client.get("/v1/places", params={"q": "mumb"}).json()
    assert body
    assert body[0]["name"] == "Mumbai"
    assert body[0]["country"] == "India"


def test_place_search_is_case_and_accent_insensitive():
    assert client.get("/v1/places", params={"q": "BENGALURU"}).json()[0]["name"] == "Bengaluru"


def test_place_search_matches_state_names():
    body = client.get("/v1/places", params={"q": "kerala"}).json()
    assert body
    assert all(p["admin"] == "Kerala" for p in body)


def test_place_search_respects_limit():
    body = client.get("/v1/places", params={"q": "a", "limit": 3}).json()
    assert len(body) <= 3


def test_place_search_empty_query_rejected():
    assert client.get("/v1/places", params={"q": ""}).status_code == 422


def test_place_search_no_match_returns_empty():
    assert client.get("/v1/places", params={"q": "zzzzzzz"}).json() == []


def test_chart_is_reproducible_across_requests():
    first = client.post("/v1/chart", json=BIRTH).json()
    second = client.post("/v1/chart", json=BIRTH).json()
    assert first == second


# --- Hindi ------------------------------------------------------------------
#
# Every Devanagari field travels beside its Latin twin rather than instead of
# it, so the app can switch language without refetching. These pin that the
# pairing actually arrives — a missing `_hi` shows up in the app as a blank row,
# which reads like a broken calculation rather than a missing translation.


def test_chart_carries_devanagari_beside_the_latin():
    body = client.post("/v1/chart", json=BIRTH).json()

    assert body["lagna"]["rashi"] == "Vrishabha"
    assert body["lagna"]["rashi_hi"] == "वृषभ"
    assert body["moon_rashi_hi"] == "कर्क"
    assert body["janma_nakshatra_hi"] == "पुष्य"
    assert body["meta"]["ayanamsa_name_hi"] == "लाहिड़ी (चित्रपक्ष)"

    for graha in body["grahas"]:
        placement = graha["placement"]
        assert placement["rashi_hi"], graha["graha"]
        assert placement["nakshatra_hi"], graha["graha"]
        assert placement["navamsa_hi"], graha["graha"]
        assert placement["rashi_lord_hi"], graha["graha"]
        assert placement["nakshatra_lord_hi"], graha["graha"]


def test_panchang_carries_devanagari_for_every_limb():
    body = client.post("/v1/panchang", json=BIRTH).json()

    assert body["paksha_hi"] == "कृष्ण"
    assert body["tithi_hi"] == "त्रयोदशी"
    assert body["vara_hi"] == "गुरुवार"
    assert body["nakshatra_hi"] == "पुष्य"
    assert body["yoga_hi"] and body["karana_hi"] and body["vara_lord_hi"]


def test_today_carries_devanagari():
    body = client.post("/v1/today", json=BIRTH).json()

    assert body["birth_moon_rashi_hi"] == "कर्क"
    assert body["birth_nakshatra_hi"] == "पुष्य"
    assert body["moon_rashi_hi"] and body["moon_nakshatra_hi"] and body["sun_rashi_hi"]
    assert body["panchang"]["tithi_hi"]


def test_a_devanagari_field_is_never_blank_and_never_alone():
    """Two failures, one test.

    A *blank* translation renders as a missing value and reads like a broken
    calculation. A translation present without its Latin twin — or the reverse —
    means one language silently shows nothing where the other shows something.

    Null on both sides is fine and deliberate: `meaning` is attached only to the
    periods a screen displays, so the rest carry neither language.
    """
    body = client.post("/v1/reading", json=BIRTH).json()

    def walk(node):
        if isinstance(node, dict):
            for key, value in node.items():
                if key.endswith("_hi"):
                    if value is not None:
                        assert isinstance(value, str) and value.strip(), key
                    twin = key[: -len("_hi")]
                    if twin in node:
                        assert (value is None) == (node[twin] is None), key
                walk(value)
        elif isinstance(node, list):
            for item in node:
                walk(item)

    walk(body)


def test_panchang_carries_the_month_the_year_and_the_four_times():
    body = client.post("/v1/panchang", json=BIRTH).json()

    assert body["masa"] and body["masa_hi"]
    # 15 August 1947 fell in Vikram Samvat 2004 — the year that had begun that
    # Chaitra, in March.
    assert body["vikram_samvat"] == 2004
    assert body["shaka_samvat"] == 1869

    # Delhi in August: the Sun rises and sets on the day asked about.
    assert body["sunrise"] is not None
    assert body["sunset"] is not None
    assert body["sunrise"] < body["sunset"]


def test_a_missing_rise_serialises_as_null_not_as_a_time():
    """Null has to survive to the client, which renders it as a dash. A
    fabricated time here would be indistinguishable from a real one."""
    january = BIRTH | {"date": "2026-01-10", "time": "12:00"}
    body = client.post("/v1/panchang", json=january).json()

    assert "moonrise" in body
    assert body["moonrise"] is None
    assert body["moonset"] is not None


# --- Matching ---------------------------------------------------------------


PARTNER = {
    "date": "1990-06-02",
    "time": "14:30",
    "latitude": 19.0760,
    "longitude": 72.8777,
    "place": "Mumbai, India",
}


def test_match_returns_eight_koots_out_of_thirty_six():
    body = client.post("/v1/match", json={"bride": BIRTH, "groom": PARTNER}).json()

    assert [k["name"] for k in body["koots"]] == [
        "varna", "vashya", "tara", "yoni", "graha_maitri", "gana", "bhakoot", "nadi",
    ]
    assert [k["maximum"] for k in body["koots"]] == [1, 2, 3, 4, 5, 6, 7, 8]
    assert body["maximum"] == 36
    assert body["total"] == sum(k["points"] for k in body["koots"])


def test_match_says_what_each_koot_was_computed_from():
    """A bare number out of 36 is the form of this that gets used against
    people. Every koot has to carry the values behind it."""
    body = client.post("/v1/match", json={"bride": BIRTH, "groom": PARTNER}).json()

    for koot in body["koots"]:
        assert koot["bride"] and koot["groom"], koot["name"]
        # Both scripts, like everything else on this API: koot names rendered
        # in Devanagari above values rendered in Latin is half a translation.
        assert koot["bride_hi"] and koot["groom_hi"], koot["name"]

    assert body["bride_nakshatra"] == "Pushya"
    assert body["bride_nakshatra_hi"] == "पुष्य"
    assert body["bride_rashi_hi"] and body["groom_rashi_hi"]


def test_match_never_returns_a_verdict():
    """No threshold, no label, no grade — see chapter 30. If a field like this
    ever appears, it was added against the product's stated position."""
    body = client.post("/v1/match", json={"bride": BIRTH, "groom": PARTNER}).json()

    forbidden = {"verdict", "compatible", "recommended", "grade", "rating", "advice"}
    assert forbidden.isdisjoint(body)
    assert forbidden.isdisjoint(set().union(*(k.keys() for k in body["koots"])))


def test_match_is_asymmetric_because_the_procedure_is():
    forward = client.post("/v1/match", json={"bride": BIRTH, "groom": PARTNER}).json()
    swapped = client.post("/v1/match", json={"bride": PARTNER, "groom": BIRTH}).json()

    varna_forward = next(k for k in forward["koots"] if k["name"] == "varna")
    varna_swapped = next(k for k in swapped["koots"] if k["name"] == "varna")
    assert (varna_forward["bride"], varna_forward["groom"]) == (
        varna_swapped["groom"],
        varna_swapped["bride"],
    )


def test_match_rejects_bad_birth_data():
    bad = {"bride": BIRTH, "groom": PARTNER | {"latitude": 120.0}}
    assert client.post("/v1/match", json=bad).status_code == 422

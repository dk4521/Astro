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

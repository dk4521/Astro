"""Tests for the course and the today endpoint.

Both are entirely deterministic — no key, no network, no model — which is the
property most worth pinning. If either ever starts calling the interpretation
layer, these tests should be the thing that notices.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import course
from app.course.models import apply_personalisation
from app.main import app

BIRTH = {
    "date": "1947-08-15",
    "time": "00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
    "place": "New Delhi",
}


@pytest.fixture(scope="module")
def client():
    return TestClient(app)


# --- Content ----------------------------------------------------------------


def test_thirty_chapters_with_unique_slugs():
    slugs = [c.slug for c in course.CHAPTERS]
    assert len(slugs) == 30
    assert len(set(slugs)) == 30


def test_every_chapter_exists_in_both_languages():
    """Hindi is not a translation afterthought; a missing string would silently
    fall back to English and nobody would notice in an English-run test."""
    for chapter in course.CHAPTERS:
        for field in (chapter.title, chapter.summary, chapter.part):
            assert field.get("en") and field.get("hi"), chapter.slug
        for section in chapter.sections:
            assert section.heading.get("en") and section.heading.get("hi"), chapter.slug
            for paragraph in section.body:
                assert paragraph.get("en") and paragraph.get("hi"), chapter.slug
            if section.aside is not None:
                assert section.aside.get("en") and section.aside.get("hi"), chapter.slug


def test_every_personalisation_runs_on_a_real_chart():
    """These read the chart directly, so a renamed engine field breaks them —
    and would otherwise only surface as a missing block on a user's screen."""
    import datetime as dt

    from app.astro import build_chart, panchang_for, vimshottari

    chart = build_chart(dt.datetime(1947, 8, 15, 0, 0), 28.6139, 77.2090)
    panchang, dasha = panchang_for(chart), vimshottari(chart, levels=3)

    for chapter in course.CHAPTERS:
        text = apply_personalisation(chapter, chart, panchang, dasha, "New Delhi")
        if text is not None:
            assert text.get("en") and text.get("hi"), chapter.slug


def test_crisis_helplines_survive_in_the_final_chapter():
    """Chapter 30 carries the same numbers as the prompt contract. If the course
    is ever trimmed, this is the line that should fail first."""
    final = course.CHAPTERS_BY_SLUG["reading-responsibly"]
    text = " ".join(
        s.aside["en"] for s in final.sections if s.aside is not None
    ) + " " + " ".join(
        s.aside["hi"] for s in final.sections if s.aside is not None
    )
    for number in ("14416", "9820466726", "181", "112"):
        assert number in text


# --- API --------------------------------------------------------------------


def test_index_is_small_and_ordered(client):
    body = client.get("/v1/course").json()
    assert len(body["chapters"]) == 30
    assert [c["number"] for c in body["chapters"]] == list(range(1, 31))
    assert body["total_minutes"] > 0
    # The index is fetched on every visit; chapter prose must not ride along.
    assert "sections" not in body["chapters"][0]


def test_index_switches_language(client):
    en = client.get("/v1/course?language=en").json()
    hi = client.get("/v1/course?language=hi").json()
    assert en["chapters"][0]["title"] != hi["chapters"][0]["title"]
    assert hi["language"] == "hi"


def test_unknown_language_falls_back_rather_than_failing(client):
    body = client.get("/v1/course?language=fr").json()
    assert body["language"] == "en"


def test_chapter_reads_without_birth_details(client):
    body = client.post("/v1/course/the-lagna", json={}).json()
    assert body["sections"]
    # No chart was sent, so there is nothing to personalise — and nothing invented.
    assert body["in_your_chart"] is None


def test_chapter_is_personalised_from_the_chart(client):
    body = client.post("/v1/course/the-lagna", json={"birth": BIRTH}).json()
    assert "Vrishabha" in body["in_your_chart"]
    assert body["next_slug"] == "reading-the-diagram"


def test_chapter_personalisation_follows_the_language(client):
    hi = client.post("/v1/course/the-lagna?language=hi", json={"birth": BIRTH}).json()
    assert "वृषभ" in hi["in_your_chart"]


def test_unknown_chapter_is_404(client):
    assert client.post("/v1/course/no-such-chapter", json={}).status_code == 404


# --- Today ------------------------------------------------------------------


def test_today_reports_now_and_the_active_period(client):
    body = client.post("/v1/today", json=BIRTH).json()

    assert body["panchang"]["tithi"]
    assert body["moon_rashi"]
    # The dasha comes from the natal chart, the panchang from this moment.
    assert body["birth_nakshatra"] == "Pushya"
    assert body["active"], "someone born in 1947 is inside the 120-year cycle"
    assert body["active"][0]["level"] == 1


def test_today_needs_no_model_credentials(client, monkeypatch):
    """The screen a user opens several times a day must not touch the quota."""
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)
    assert client.post("/v1/today", json=BIRTH).status_code == 200
    assert client.get("/v1/course").status_code == 200

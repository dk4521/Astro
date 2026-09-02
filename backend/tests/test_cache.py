"""Tests for the interpretation cache.

The free tier allows 20 requests per model per day, so these are not
optimisation tests — a cache that quietly stopped working would take the app
back to unusable without anything failing. Two properties matter most and are
tested from both directions: an identical request must not reach the model, and
a request that differs in *any* way that could change the answer must.
"""

from __future__ import annotations

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.ai import cache, interpret
from app.ai.client import Request
from app.ai.interpret import Turn
from app.ai.prompts import READING_REQUEST, reading_directive
from app.astro import build_chart
from app import main
from app.main import app

DELHI = dict(birth_local=dt.datetime(1947, 8, 15, 0, 0), latitude=28.6139, longitude=77.2090)
MUMBAI = dict(birth_local=dt.datetime(1990, 6, 2, 14, 30), latitude=19.0760, longitude=72.8777)

API_BIRTH = {"date": "1947-08-15", "time": "00:00", "latitude": 28.6139, "longitude": 77.2090}

# Fixed so the fact brief — which carries `as of:` at day precision — does not
# change underneath a test that happens to run across midnight.
AS_OF = dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)


@pytest.fixture(scope="module")
def chart():
    return build_chart(**DELHI)


class CountingClient:
    """Counts model calls, so 'did not reach the model' is an assertion."""

    def __init__(self, reply: str = "A calm, grounded reading.") -> None:
        self.reply = reply
        self.calls = 0

    def complete(self, request: Request) -> str:
        self.calls += 1
        return self.reply

    def stream(self, request: Request):
        self.calls += 1
        for word in self.reply.split(" "):
            yield word + " "


class FailingStream(CountingClient):
    """Streams a few words and then dies, the way a dropped connection does."""

    def stream(self, request: Request):
        self.calls += 1
        yield "The first half "
        raise RuntimeError("connection lost")


@pytest.fixture
def model(monkeypatch):
    client = CountingClient()
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: client)
    return client


# --- Reuse ------------------------------------------------------------------


def test_identical_reading_does_not_reach_the_model(chart, model):
    first = interpret.reading(chart, language="en", as_of=AS_OF)
    second = interpret.reading(chart, language="en", as_of=AS_OF)

    assert model.calls == 1
    assert second.text == first.text
    assert first.cached is False
    assert second.cached is True


def test_a_cached_answer_is_still_checked_against_the_chart(chart, model):
    """Grounding runs on the way out, not once at the time of storage.

    Nothing ungrounded is stored in the first place, so this seeds the cache
    directly to reach the case that matters: an entry stored under one version
    of the grounding rules, read back under a stricter one. The check has to be
    on the read path or the oldest answers would be the ones that escape it.
    """
    request = interpret._build_request(
        chart, READING_REQUEST, "en", AS_OF, reading_directive("en")
    )
    cache.put(request, "Your Moon is in Simha, which shapes everything.")

    result = interpret.reading(chart, language="en", as_of=AS_OF)

    assert model.calls == 0, "the seeded entry should have been used"
    assert result.cached is True
    assert result.model_grounded is False
    assert "Simha" in result.contradictions[0]


def test_an_ungrounded_reading_is_never_stored(chart, monkeypatch):
    """A reading that contradicts the chart gets a retry, not a second airing.

    Without this the cache would take the product's one visible failure — an
    answer that disagrees with the computed chart — and repeat it verbatim to
    the same reader for a day.
    """
    client = CountingClient("Your Moon is in Simha, which shapes everything.")
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: client)

    first = interpret.reading(chart, language="en", as_of=AS_OF)
    second = interpret.reading(chart, language="en", as_of=AS_OF)

    assert first.model_grounded is False
    assert client.calls == 2, "the model should have been asked again"
    assert second.cached is False
    assert cache.stats().entries == 0


def test_an_ungrounded_streamed_answer_is_never_stored(chart, monkeypatch):
    client = CountingClient("Your Moon is in Simha, so this period is loud.")
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: client)

    list(interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF))
    list(interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF))

    assert client.calls == 2
    assert cache.stats().entries == 0


# --- What must miss ---------------------------------------------------------


def test_another_language_is_a_different_request(chart, model):
    interpret.reading(chart, language="en", as_of=AS_OF)
    interpret.reading(chart, language="hi", as_of=AS_OF)

    assert model.calls == 2


def test_another_chart_is_a_different_request(model):
    interpret.reading(build_chart(**DELHI), language="en", as_of=AS_OF)
    interpret.reading(build_chart(**MUMBAI), language="en", as_of=AS_OF)

    assert model.calls == 2


def test_another_day_is_a_different_request(chart, model):
    """The brief carries the date, so a new day misses without a TTL doing it.

    This is the property that lets the cache be keyed on the request alone: the
    running dasha is part of what the model was told, so an answer about "this
    period" can never be served for a different one.
    """
    interpret.reading(chart, language="en", as_of=AS_OF)
    interpret.reading(chart, language="en", as_of=AS_OF + dt.timedelta(days=1))

    assert model.calls == 2


def test_another_question_is_a_different_request(chart, model):
    interpret.answer(chart, "What about work?", language="en", as_of=AS_OF)
    interpret.answer(chart, "What about family?", language="en", as_of=AS_OF)

    assert model.calls == 2


def test_the_same_question_after_different_history_is_a_different_request(chart, model):
    interpret.answer(chart, "And now?", language="en", as_of=AS_OF)
    interpret.answer(
        chart,
        "And now?",
        language="en",
        as_of=AS_OF,
        history=[Turn(role="user", content="Tell me about my Moon.")],
    )

    assert model.calls == 2


def test_a_changed_prompt_or_model_invalidates_everything(chart, model, monkeypatch):
    """The system prompt and model chain are in the key, not merely nearby.

    Without this, editing the prompt contract would leave every reader being
    served answers generated under the old one until the process restarted.
    """
    interpret.reading(chart, language="en", as_of=AS_OF)
    monkeypatch.setattr("app.ai.client.MODEL", "gemini-some-other-model")
    interpret.reading(chart, language="en", as_of=AS_OF)

    assert model.calls == 2


# --- Streaming --------------------------------------------------------------


def test_a_streamed_answer_is_cached_whole(chart, model):
    first = "".join(interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF))
    second = "".join(interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF))

    assert model.calls == 1
    assert second == first


def test_an_interrupted_stream_is_not_cached(chart, monkeypatch):
    """Half an answer must never be stored and then served as the whole one."""
    client = FailingStream()
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: client)

    with pytest.raises(RuntimeError):
        list(interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF))

    assert cache.stats().entries == 0


def test_an_abandoned_stream_is_not_cached(chart, model):
    """A reader who leaves mid-answer leaves nothing behind either."""
    stream = interpret.stream_answer(chart, "Why?", language="en", as_of=AS_OF)
    next(stream)
    stream.close()

    assert cache.stats().entries == 0


# --- The store itself -------------------------------------------------------


def _request(text: str) -> Request:
    return Request(messages=[{"role": "user", "content": text}])


def test_an_empty_answer_is_not_stored():
    cache.put(_request("q"), "   ")
    assert cache.get(_request("q")) is None


def test_entries_expire(monkeypatch):
    monkeypatch.setattr(cache, "TTL_SECONDS", -1.0)
    cache.put(_request("q"), "an answer")
    assert cache.get(_request("q")) is None


def test_the_oldest_entry_is_evicted_first(monkeypatch):
    monkeypatch.setattr(cache, "SIZE", 2)
    cache.put(_request("one"), "1")
    cache.put(_request("two"), "2")
    cache.get(_request("one"))  # touched, so "two" is now the coldest
    cache.put(_request("three"), "3")

    assert cache.get(_request("one")) == "1"
    assert cache.get(_request("two")) is None
    assert cache.get(_request("three")) == "3"


def test_a_zero_size_disables_the_cache(monkeypatch):
    monkeypatch.setattr(cache, "SIZE", 0)
    cache.put(_request("q"), "an answer")
    assert cache.get(_request("q")) is None


def test_the_key_does_not_depend_on_dict_ordering():
    """Keys must survive a restart, so nothing salted or order-dependent.

    Python hashes strings with a per-process salt and preserves insertion order
    in dicts; a key built from either would be a key that silently stops
    matching the moment the service redeploys.
    """
    first = Request(messages=[{"role": "user", "content": "hello"}])
    second = Request(messages=[{"content": "hello", "role": "user"}])

    assert cache.key_for(first) == cache.key_for(second)


# --- Reported to the outside ------------------------------------------------


def test_the_endpoint_reports_hit_or_miss(monkeypatch):
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: CountingClient())
    monkeypatch.setattr("app.api.routes.ai.is_configured", lambda: True)
    client = TestClient(app)

    first = client.post("/v1/interpret", json={"birth": API_BIRTH, "language": "en"})
    second = client.post("/v1/interpret", json={"birth": API_BIRTH, "language": "en"})

    assert first.status_code == 200
    assert first.headers["X-Cache"] == "miss"
    assert second.headers["X-Cache"] == "hit"
    assert second.json()["text"] == first.json()["text"]


def test_health_reports_cache_reuse(chart, model, monkeypatch):
    interpret.reading(chart, language="en", as_of=AS_OF)
    interpret.reading(chart, language="en", as_of=AS_OF)

    # The stats left `/health` when it stopped answering "is the paywall on"
    # to anyone who asked. They now need the operator's token.
    monkeypatch.setattr(main, "_METRICS_TOKEN", "t0ken")
    body = TestClient(app).get("/v1/health/cache", params={"token": "t0ken"}).json()
    assert body["hits"] == 1
    assert body["misses"] == 1
    assert body["entries"] == 1
    assert body["ratio"] == 0.5


def test_the_gazetteer_is_cacheable_by_http():
    response = TestClient(app).get("/v1/places", params={"q": "Delhi"})
    assert "max-age" in response.headers["Cache-Control"]


def test_the_course_index_is_cacheable_by_http():
    response = TestClient(app).get("/v1/course", params={"language": "en"})
    assert "max-age" in response.headers["Cache-Control"]

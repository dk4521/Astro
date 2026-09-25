"""Tests for the interpretation layer.

No API key and no network. A stub client stands in for the model, which lets
these tests assert the things that actually matter here: that the model is
handed the chart and nothing but the chart, that the prompt contract reaches it
intact, and that the grounding check catches a fabricated placement.
"""

from __future__ import annotations

import datetime as dt

import pytest
from fastapi.testclient import TestClient

from app.ai import grounding, interpret, set_client
from app.ai.client import Request
from app.ai.facts import build_brief
from app.ai.prompts import SYSTEM_PROMPT
from app.astro import build_chart, panchang_for, vimshottari
from app.main import app

BIRTH = {"birth_local": dt.datetime(1947, 8, 15, 0, 0), "latitude": 28.6139, "longitude": 77.2090}

API_BIRTH = {
    "date": "1947-08-15",
    "time": "00:00",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


@pytest.fixture(scope="module")
def chart():
    return build_chart(**BIRTH)


class StubClient:
    """Records the request it was given and replies with canned text."""

    def __init__(self, reply: str = "A calm, grounded reading.") -> None:
        self.reply = reply
        self.requests: list[Request] = []

    def complete(self, request: Request) -> str:
        self.requests.append(request)
        return self.reply

    def stream(self, request: Request):
        self.requests.append(request)
        for word in self.reply.split(" "):
            yield word + " "


@pytest.fixture
def stub():
    client = StubClient()
    set_client(client)
    yield client
    set_client(None)


# --- The fact brief ---------------------------------------------------------


def test_brief_contains_every_graha(chart):
    brief = build_brief(
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    )
    for graha in chart.grahas:
        assert graha in brief


def test_brief_states_positions_the_model_would_otherwise_guess(chart):
    brief = build_brief(
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    )
    assert "Vrishabha" in brief          # lagna
    assert "Pushya" in brief             # janma nakshatra
    assert "Krishna Trayodashi" in brief  # tithi
    assert "Saturn" in brief             # first mahadasha lord
    assert "whole-sign" in brief         # provenance
    assert "Lahiri" in brief


def test_brief_marks_retrograde_and_combust(chart):
    brief = build_brief(
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.UTC)
    )
    assert "retrograde" in brief   # Rahu and Ketu always are
    assert "combust" in brief      # Venus and Saturn are, in this chart


def test_brief_reports_the_current_dasha(chart):
    brief = build_brief(
        chart,
        panchang_for(chart),
        vimshottari(chart, levels=3),
        dt.datetime(1990, 1, 1, tzinfo=dt.UTC),
    )
    assert "Mahadasha" in brief
    assert "Antardasha" in brief
    assert "running now" in brief


# --- What reaches the model -------------------------------------------------


def test_model_receives_the_chart_and_the_contract(chart, stub):
    interpret.reading(chart, language="en")

    request = stub.requests[0]
    sent = request.messages[0]["content"]

    # The chart facts are in the message the model reads.
    assert "=== COMPUTED CHART DATA ===" in sent
    assert "Vrishabha" in sent
    # And the contract is the system prompt, not something inlined per request.
    assert "translate" in SYSTEM_PROMPT.lower()


def test_language_directive_stays_out_of_the_cached_prompt(chart, stub):
    """Language varies per request; the cached prefix must not.

    Prompt caching is a prefix match, so folding the language choice into the
    system prompt would invalidate the cache every time a user switched.
    """
    interpret.reading(chart, language="hi")
    interpret.reading(chart, language="en")

    hindi, english = stub.requests
    assert hindi.suffix != english.suffix
    assert "Hindi" in hindi.suffix
    assert "English" in english.suffix


def test_conversation_history_is_replayed(chart, stub):
    history = [
        interpret.Turn(role="user", content="What about my career?"),
        interpret.Turn(role="assistant", content="Your 10th house is Kumbha."),
    ]
    interpret.answer(chart, "And relationships?", language="en", history=history)

    messages = stub.requests[0].messages
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    # The chart rides on the first turn so later turns share it as a stable prefix.
    assert "COMPUTED CHART DATA" in messages[0]["content"]
    assert messages[-1]["content"] == "And relationships?"


def test_conversation_history_discards_leading_assistant_turn(chart, stub):
    history = [
        interpret.Turn(role="assistant", content="An old answer."),
        interpret.Turn(role="user", content="What about my career?"),
        interpret.Turn(role="assistant", content="Your 10th house is Kumbha."),
    ]
    interpret.answer(chart, "And relationships?", language="en", history=history)

    messages = stub.requests[0].messages
    assert [m["role"] for m in messages] == ["user", "assistant", "user"]
    assert "An old answer." not in messages[0]["content"]


def test_streaming_yields_chunks(chart, stub):
    chunks = list(interpret.stream_answer(chart, "Tell me about Saturn", language="en"))
    assert len(chunks) > 1
    assert "".join(chunks).strip() == stub.reply


# --- Grounding --------------------------------------------------------------


def test_accurate_statement_passes(chart):
    text = "Your Moon is in Karka, in the Pushya nakshatra, and it sits in house 3."
    assert grounding.check(text, chart) == []


def test_fabricated_rashi_is_caught(chart):
    text = "Your Moon is in Simha, which gives you a natural warmth."
    found = grounding.check(text, chart)

    assert len(found) == 1
    assert found[0].graha == "Moon"
    assert found[0].asserted == "Simha"
    assert found[0].actual == "Karka"
    assert found[0].kind == "rashi"


def test_grounding_skips_unavailable_claim_extraction(chart, monkeypatch):
    monkeypatch.setattr(grounding, "extract_claims", lambda text: None)
    assert grounding.check("Jupiter is in Aries.", chart) == []


def test_devanagari_prose_makes_no_claim(chart):
    """The crisis path names grahas in order to refuse; that is not a reading."""
    assert grounding.check("कोई भी ग्रह किसी से हिंसा नहीं करवाता।", chart) == []
    assert grounding.check("यह समय धैर्य मांगता है, इसमें कोई चेतावनी नहीं है।", chart) == []


def test_interpretation_flags_ungrounded_output(chart):
    set_client(StubClient("Your Moon is in Simha, which shapes everything."))
    try:
        result = interpret.reading(chart, language="en")
    finally:
        set_client(None)

    assert result.grounding_status == 'CONTRADICTORY_CLAIM'
    assert len(result.contradictions) == 1
    assert "Simha" in result.contradictions[0]
    assert "Karka" in result.contradictions[0]


def test_interpretation_passes_clean_output(chart, stub):
    result = interpret.reading(chart, language="en")
    assert result.grounding_status != 'CONTRADICTORY_CLAIM'
    assert result.contradictions == []


def test_grounding_ignores_unrelated_prose(chart):
    """The check must not fire on text making no placement claim."""
    text = (
        "This period asks for patience. Nothing here is a warning, and none of "
        "it decides anything for you."
    )
    assert grounding.check(text, chart) == []


# --- HTTP surface -----------------------------------------------------------


def test_interpret_endpoint(stub):
    client = TestClient(app)
    response = client.post(
        "/v1/interpret", json={"birth": API_BIRTH, "language": "en"}
    )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == stub.reply
    assert body["grounding_status"] != "CONTRADICTORY_CLAIM"
    assert body["language"] == "en"


def test_interpret_endpoint_reports_ungrounded_text():
    set_client(StubClient("Your Moon is in Simha."))
    try:
        response = TestClient(app).post("/v1/interpret", json={"birth": API_BIRTH})
    finally:
        set_client(None)

    body = response.json()
    assert body["grounding_status"] == "CONTRADICTORY_CLAIM"
    assert body["contradictions"]


def test_chat_endpoint_streams_then_reports_grounding(stub):
    client = TestClient(app)
    response = client.post(
        "/v1/chat",
        json={"birth": API_BIRTH, "question": "What is my Moon doing?", "language": "en"},
    )

    assert response.status_code == 200
    assert response.headers["content-type"].startswith("text/event-stream")

    body = response.text
    assert "event: token" in body
    # Exactly one terminal event, and it carries the verdict.
    assert body.count("event: done") == 1
    assert '"grounding_status": "TRADITIONAL_INTERPRETATION"' in body


def test_chat_rejects_an_empty_question(stub):
    response = TestClient(app).post(
        "/v1/chat", json={"birth": API_BIRTH, "question": ""}
    )
    assert response.status_code == 422


def test_interpretation_endpoints_fail_clearly_without_credentials(monkeypatch):
    """A missing key must be a legible 503, not an SDK stack trace."""
    set_client(None)
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.delenv("GOOGLE_API_KEY", raising=False)

    response = TestClient(app).post("/v1/interpret", json={"birth": API_BIRTH})
    assert response.status_code == 503
    assert "not configured" in response.json()["detail"]


# --- Gemini specifics -------------------------------------------------------
#
# These cover the two behaviours the provider port introduced. Both fail
# silently rather than loudly if they regress: a wrong role name is rejected by
# the API mid-conversation, and an unchecked safety block returns empty text
# that reads as a successful but blank reading.


class _FakeCandidate:
    def __init__(self, finish_reason=None):
        self.finish_reason = finish_reason


class _FakeReason:
    def __init__(self, name):
        self.name = name


class _FakeFeedback:
    def __init__(self, block_reason):
        self.block_reason = block_reason


class _FakeResponse:
    def __init__(self, text="ok", candidates=None, prompt_feedback=None):
        self.text = text
        self.candidates = candidates if candidates is not None else [_FakeCandidate()]
        self.prompt_feedback = prompt_feedback


def _bare_client():
    """A GeminiClient with the SDK wired up but no network calls made."""
    from google.genai import types

    from app.ai.client import GeminiClient

    client = GeminiClient.__new__(GeminiClient)
    client._types = types
    client._errors = (RuntimeError,)
    return client


def test_assistant_turns_are_renamed_for_gemini():
    """Gemini calls the assistant turn "model" and rejects "assistant"."""
    from app.ai.client import Request

    client = _bare_client()
    contents = client._contents(
        Request(
            messages=[
                {"role": "user", "content": "hi"},
                {"role": "assistant", "content": "hello"},
                {"role": "user", "content": "again"},
            ]
        )
    )

    assert [c.role for c in contents] == ["user", "model", "user"]
    assert contents[0].parts[0].text == "hi"


def test_language_directive_rides_the_system_instruction():
    from app.ai.client import _system_instruction

    combined = _system_instruction("Respond in English.")
    assert combined.startswith(SYSTEM_PROMPT)
    assert combined.endswith("Respond in English.")
    assert _system_instruction(None) == SYSTEM_PROMPT


def test_blocked_prompt_raises():
    from app.ai.client import InterpretationBlocked

    client = _bare_client()
    response = _FakeResponse(prompt_feedback=_FakeFeedback("SAFETY"))

    with pytest.raises(InterpretationBlocked, match="request was blocked"):
        client._check(response)


def test_blocked_completion_raises():
    """A withheld answer arrives as a finish_reason, not an exception."""
    from app.ai.client import InterpretationBlocked

    client = _bare_client()
    response = _FakeResponse(candidates=[_FakeCandidate(_FakeReason("SAFETY"))])

    with pytest.raises(InterpretationBlocked, match="withheld"):
        client._check(response)


def test_empty_candidates_raise():
    from app.ai.client import InterpretationUnavailable

    client = _bare_client()
    with pytest.raises(InterpretationUnavailable, match="no response"):
        client._check(_FakeResponse(candidates=[]))


def test_normal_completion_passes_the_check():
    client = _bare_client()
    client._check(_FakeResponse(candidates=[_FakeCandidate(_FakeReason("STOP"))]))


def test_blocked_is_an_unavailable():
    """Routes catch InterpretationUnavailable; a block must not escape it."""
    from app.ai.client import InterpretationBlocked, InterpretationUnavailable

    assert issubclass(InterpretationBlocked, InterpretationUnavailable)


def test_crisis_support_is_in_the_contract():
    """The crisis path is why DANGEROUS_CONTENT is relaxed — pin both together."""
    assert "14416" in SYSTEM_PROMPT       # Tele-MANAS
    assert "9820466726" in SYSTEM_PROMPT  # AASRA
    assert "181" in SYSTEM_PROMPT         # Women Helpline
    assert "112" in SYSTEM_PROMPT         # emergency, India
    assert "crisis" in SYSTEM_PROMPT.lower()

    import inspect

    from app.ai.client import GeminiClient

    source = inspect.getsource(GeminiClient.__init__)
    assert "HARM_CATEGORY_DANGEROUS_CONTENT" in source
    assert "BLOCK_ONLY_HIGH" in source


def test_crisis_overrides_the_chart_question():
    """The live check found the model answering the chart question anyway.

    `scripts/check_crisis_path.py` caught a full dasha reading appended to an
    otherwise correct crisis reply — acknowledgement, helpline, then "Jupiter
    sits in your 6th house". The contract now says the support is the whole
    reply; this pins that it still says so, since the sentence is the only
    defence and deleting it would break nothing visible offline.
    """
    contract = SYSTEM_PROMPT.lower()
    assert "overrides every other instruction" in contract
    assert "the support is the entire reply" in contract


# --- Model fallback and thinking level --------------------------------------
#
# Free-tier capacity is the dominant runtime failure. These pin the recovery
# logic, which is otherwise only exercised when Google is busy.


def test_capacity_errors_are_retryable_elsewhere():
    """503 and 429 are one model's problem; a 400 is the request's."""
    from google.genai import errors

    from app.ai.client import GeminiClient

    def api_error(code, status):
        payload = {"error": {"code": code, "message": "x", "status": status}}

        class Resp:
            def __init__(self):
                self.headers = {}

            def json(self):
                return payload

        cls = errors.ServerError if code >= 500 else errors.ClientError
        return cls(code, payload, Resp())

    assert GeminiClient._is_capacity_error(api_error(503, "UNAVAILABLE"))
    assert GeminiClient._is_capacity_error(api_error(429, "RESOURCE_EXHAUSTED"))
    # A malformed request or a rejected key fails identically on every model,
    # so walking the chain would only waste time.
    assert not GeminiClient._is_capacity_error(api_error(400, "INVALID_ARGUMENT"))
    assert not GeminiClient._is_capacity_error(api_error(404, "NOT_FOUND"))


def test_model_chain_has_no_repeats():
    from app.ai import client as C

    chain = C._model_chain()
    assert chain[0] == C.MODEL
    assert len(chain) == len(set(chain))


def test_thinking_level_avoids_models_that_reject_it():
    """gemini-3.7-flash returns 400 for MINIMAL; predict it, don't discover it."""
    from app.ai import client as C

    if C.THINKING_LEVEL != "MINIMAL":
        pytest.skip("only meaningful when MINIMAL is configured")

    assert C.GeminiClient._thinking_for("gemini-3.7-flash") == "LOW"
    assert C.GeminiClient._thinking_for("gemini-3.5-flash") == "MINIMAL"


def test_truncation_is_raised_not_returned():
    """A cut-off reading must fail loudly, not read as a finished one."""
    from app.ai.client import InterpretationTruncated

    client = _bare_client()
    response = _FakeResponse(candidates=[_FakeCandidate(_FakeReason("MAX_TOKENS"))])

    with pytest.raises(InterpretationTruncated, match="cut off"):
        client._check(response)


def test_streaming_tolerates_a_metadata_only_chunk():
    """A stream's trailing chunk can carry usage and no candidates."""
    client = _bare_client()
    client._check(_FakeResponse(candidates=[]), streaming=True)

    from app.ai.client import InterpretationUnavailable

    with pytest.raises(InterpretationUnavailable):
        client._check(_FakeResponse(candidates=[]), streaming=False)


def test_token_budget_leaves_room_for_thinking():
    """Thinking is drawn from max_output_tokens; a reading needs ~1700 total."""
    from app.ai import client as C

    assert C.MAX_TOKENS >= 4000


# --- The daily tip ----------------------------------------------------------


def test_the_tip_brief_carries_the_day_and_the_period_but_not_the_chart(chart, stub):
    """A one-line tip handed a whole natal chart reaches for a placement.

    So it is handed less: the day everyone is in, and the period this reader is
    in. Pinning the *absence* of the graha table is the point — a future
    refactor that "helpfully" swaps in `build_brief` would silently reintroduce
    the failure the short brief exists to prevent.
    """
    interpret.daily_tip(chart, chart, language="en", companion="Priya")

    brief = stub.requests[0].messages[0]["content"]
    assert "TODAY" in brief
    assert "VIMSHOTTARI DASHA" in brief
    assert "GRAHAS" not in brief
    assert "HOUSES" not in brief


def test_the_tip_speaks_as_the_companion(stub, chart):
    interpret.daily_tip(chart, chart, language="hinglish", companion="Priya")
    assert "You are Priya" in stub.requests[0].suffix

    stub.requests.clear()
    interpret.daily_tip(chart, chart, language="en", companion=None)
    assert "You are" not in stub.requests[0].suffix


def test_the_tip_refuses_to_rank_the_day_in_every_language_it_speaks():
    """The rule the model actually broke, and where it broke.

    A live run produced "aaj ka din baaton ko saaf karne ke liye achha hai" —
    a ranked day, in Hindi, from a directive that had already forbidden it in
    English. It binds now because it is stated last and in all three languages;
    this pins that it stays stated, since deleting it breaks nothing offline.
    """
    from app.ai.prompts import tip_directive

    directive = tip_directive("hi", "Meera")
    assert "never rank the day" in directive.lower()
    for banned in ("good day", "अच्छा दिन", "शुभ", "achha din", "best hai"):
        assert banned in directive
    # Stated last: everything above it is the part that loses in a long prompt.
    assert directive.rstrip().endswith("and stop there.")


def test_the_tip_endpoint_returns_a_line(stub):
    response = TestClient(app).post(
        "/v1/tip",
        json={"birth": API_BIRTH, "language": "hinglish", "companion": "Priya"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["text"] == stub.reply
    assert body["companion"] == "Priya"
    assert body["grounding_status"] != "CONTRADICTORY_CLAIM"


def test_the_tip_endpoint_reports_whether_it_was_cached(monkeypatch):
    """The home screen opens on this. Two launches must cost one request."""
    from tests.test_cache import CountingClient

    client_ = CountingClient()
    monkeypatch.setattr("app.ai.interpret.get_client", lambda: client_)
    monkeypatch.setattr("app.api.routes.ai.is_configured", lambda: True)
    api = TestClient(app)

    body = {"birth": API_BIRTH, "language": "en", "companion": "Priya"}
    first = api.post("/v1/tip", json=body)
    second = api.post("/v1/tip", json=body)

    assert first.headers["X-Cache"] == "miss"
    assert second.headers["X-Cache"] == "hit"
    assert client_.calls == 1

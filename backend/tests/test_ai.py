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

BIRTH = dict(birth_local=dt.datetime(1947, 8, 15, 0, 0), latitude=28.6139, longitude=77.2090)

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
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    )
    for graha in chart.grahas:
        assert graha in brief


def test_brief_states_positions_the_model_would_otherwise_guess(chart):
    brief = build_brief(
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    )
    assert "Vrishabha" in brief          # lagna
    assert "Pushya" in brief             # janma nakshatra
    assert "Krishna Trayodashi" in brief  # tithi
    assert "Saturn" in brief             # first mahadasha lord
    assert "whole-sign" in brief         # provenance
    assert "Lahiri" in brief


def test_brief_marks_retrograde_and_combust(chart):
    brief = build_brief(
        chart, panchang_for(chart), vimshottari(chart), dt.datetime(2026, 1, 1, tzinfo=dt.timezone.utc)
    )
    assert "retrograde" in brief   # Rahu and Ketu always are
    assert "combust" in brief      # Venus and Saturn are, in this chart


def test_brief_reports_the_current_dasha(chart):
    brief = build_brief(
        chart,
        panchang_for(chart),
        vimshottari(chart, levels=3),
        dt.datetime(1990, 1, 1, tzinfo=dt.timezone.utc),
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


def test_fabricated_nakshatra_is_caught(chart):
    found = grounding.check("Your Moon is in Rohini nakshatra.", chart)
    assert [c.kind for c in found] == ["nakshatra"]
    assert found[0].actual == "Pushya"


def test_fabricated_house_is_caught(chart):
    found = grounding.check("Saturn sits in your 7th house.", chart)
    assert [c.kind for c in found] == ["house"]
    assert found[0].actual == "3"


def test_english_sign_names_are_recognised(chart):
    """Output may use either naming system; both must be checkable."""
    assert grounding.check("Your Moon is in Cancer.", chart) == []
    assert grounding.check("Your Moon is in Leo.", chart) != []


def test_sanskrit_graha_names_are_recognised(chart):
    """Hindi and Hinglish replies name grahas in Sanskrit."""
    assert grounding.check("Aapka Chandra Karka mein hai.", chart) == []
    assert grounding.check("Aapka Chandra Simha mein hai.", chart) != []
    assert grounding.check("Shani Karka mein hai.", chart) == []


def test_several_errors_are_all_reported(chart):
    text = "Your Sun is in Mesha, your Moon is in Tula, and Mars is in Meena."
    assert len(grounding.check(text, chart)) == 3


def test_interpretation_flags_ungrounded_output(chart):
    set_client(StubClient("Your Moon is in Simha, which shapes everything."))
    try:
        result = interpret.reading(chart, language="en")
    finally:
        set_client(None)

    assert result.model_grounded is False
    assert len(result.contradictions) == 1
    assert "Simha" in result.contradictions[0]
    assert "Karka" in result.contradictions[0]


def test_interpretation_passes_clean_output(chart, stub):
    result = interpret.reading(chart, language="en")
    assert result.model_grounded is True
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
    assert body["grounded"] is True
    assert body["language"] == "en"


def test_interpret_endpoint_reports_ungrounded_text():
    set_client(StubClient("Your Moon is in Simha."))
    try:
        response = TestClient(app).post("/v1/interpret", json={"birth": API_BIRTH})
    finally:
        set_client(None)

    body = response.json()
    assert body["grounded"] is False
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
    assert '"grounded": true' in body


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
    from app.ai.client import Request, _system_instruction

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
    assert "crisis" in SYSTEM_PROMPT.lower()

    from app.ai.client import GeminiClient
    import inspect

    source = inspect.getsource(GeminiClient.__init__)
    assert "HARM_CATEGORY_DANGEROUS_CONTENT" in source
    assert "BLOCK_ONLY_HIGH" in source


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
            headers = {}

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

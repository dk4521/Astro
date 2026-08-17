"""Gemini client for the interpretation layer.

The only file in the app that knows which model provider is in use. Everything
above it — the prompt contract, the fact brief, grounding, the endpoints —
works against the `MessageClient` protocol and would survive another provider
swap untouched.

Provider history: this layer was first written against Claude Opus 5 and moved
to Gemini for its free tier. `prompts.py` still carries some phrasing tuned for
the earlier model and is due a pass once there is a real key to test against.
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from dataclasses import dataclass, field
from typing import Any, Protocol

from .prompts import SYSTEM_PROMPT

# Not the newest Flash model, deliberately. gemini-3.7-flash was tried first and
# lost on both axes that matter here: it was the most capacity-starved on the
# free tier, and it rejects the MINIMAL thinking level that makes readings feel
# instant. 3.5-flash produces readings of the same quality for this task, which
# is explanation rather than reasoning.
MODEL = os.environ.get("ASTRO_MODEL", "gemini-3.5-flash")

# Free-tier capacity is the dominant failure mode, not a rare one: during the
# first live testing session roughly half of all calls came back 503
# "experiencing high demand", and the newest model was the worst affected. The
# SDK's own retries do not help — the capacity is simply not there at that
# moment — so the recovery is to ask a different model. Ordered most to least
# capable; the first one that answers wins.
FALLBACK_MODELS = [
    name.strip()
    for name in os.environ.get(
        "ASTRO_FALLBACK_MODELS", "gemini-3.6-flash,gemini-3.5-flash-lite"
    ).split(",")
    if name.strip()
]


def _model_chain() -> list[str]:
    """The models to try, in order, without repeats."""
    chain = [MODEL]
    chain += [name for name in FALLBACK_MODELS if name not in chain]
    return chain


# Thinking tokens are drawn from `max_output_tokens`, not budgeted separately.
# Measured on gemini-3.5-flash, a reading spends ~1300 tokens thinking and ~400
# answering, so a 2000 ceiling truncated readings mid-sentence and reported
# finish_reason=MAX_TOKENS rather than failing. 8000 leaves the answer room it
# will never need; `_check` catches the case anyway.
MAX_TOKENS = int(os.environ.get("ASTRO_MAX_TOKENS", "8000"))

# Explaining settled data is not a reasoning problem, and thinking dominates
# both latency and the token budget. Measured on gemini-3.5-flash with the same
# question: LOW took 24.8s to the first streamed token and 26.1s in total;
# MINIMAL took 1.8s and 5.5s, with no loss of depth in the answer. Since the
# reader watches a blank screen until the first token, that difference is the
# whole feel of the product.
#
# gemini-3.7-flash rejects MINIMAL with a 400 — see `_thinking_for` below.
THINKING_LEVEL = os.environ.get("ASTRO_THINKING_LEVEL", "MINIMAL")

# Models that reject the configured level and need the next one up.
_NO_MINIMAL = frozenset({"gemini-3.7-flash"})

# Astrology invites florid prose. A low temperature keeps readings grounded and
# repeatable enough that two users with similar charts get consistent framing.
TEMPERATURE = float(os.environ.get("ASTRO_TEMPERATURE", "0.7"))


class InterpretationUnavailable(RuntimeError):
    """The model could not be reached, or its answer was withheld."""


class InterpretationTruncated(InterpretationUnavailable):
    """The model ran out of output budget mid-answer.

    Its own class because the failure is silent otherwise: the API returns a
    plausible-looking reading that simply stops mid-sentence. With the current
    budget this should never fire — if it does, `MAX_TOKENS` or
    `THINKING_LEVEL` needs revisiting rather than the user seeing half a
    sentence.
    """


class InterpretationBlocked(InterpretationUnavailable):
    """A safety filter withheld the response.

    Separated from the general failure because it needs different handling: the
    request itself was fine, and the most likely trigger is the crisis-support
    path — someone in distress getting a blank screen is the worst outcome this
    product has. See `_SAFETY` below.
    """


class MessageClient(Protocol):
    """The slice of the provider SDK this package uses.

    A Protocol rather than a base class so a stub needs no import, and so the
    provider stays replaceable in one file.
    """

    def complete(self, request: "Request") -> str: ...

    def stream(self, request: "Request") -> Iterator[str]: ...


@dataclass(frozen=True, slots=True)
class Request:
    """One interpretation request, independent of provider.

    `messages` uses `role` values of "user" and "assistant"; translating those
    to whatever the provider calls them is this module's job, not the caller's.
    """

    messages: list[dict[str, Any]] = field(default_factory=list)
    # Per-request instructions kept out of the shared system prompt — language
    # choice above all, so a stable prefix stays stable across users.
    suffix: str | None = None
    max_tokens: int = MAX_TOKENS


def _system_instruction(suffix: str | None) -> str:
    return f"{SYSTEM_PROMPT}\n\n{suffix}" if suffix else SYSTEM_PROMPT


class GeminiClient:
    """Live client. Constructed lazily so importing this module needs no key."""

    def __init__(self, api_key: str | None = None) -> None:
        try:
            from google import genai
            from google.genai import types
        except ImportError as exc:  # pragma: no cover - dependency is declared
            raise InterpretationUnavailable(
                "the `google-genai` package is not installed"
            ) from exc

        self._types = types
        self._errors = self._error_types()

        key = api_key or os.environ.get("GEMINI_API_KEY") or os.environ.get(
            "GOOGLE_API_KEY"
        )
        if not key:
            raise InterpretationUnavailable("GEMINI_API_KEY is not set")

        self._client = genai.Client(api_key=key)

        # Gemini's own filters sit in front of ours. Two categories are relaxed
        # to BLOCK_ONLY_HIGH rather than left at their defaults:
        #
        #   DANGEROUS_CONTENT — the crisis path in SYSTEM_PROMPT deliberately
        #     engages with self-harm in order to redirect someone to real help.
        #     A filter tuned to block any mention of it would silence exactly
        #     the response that matters most.
        #   HARASSMENT — readings routinely discuss difficult family and
        #     relationship dynamics, which reads as conflict to a strict filter.
        #
        # This loosens a second line of defence, not the first: the prompt
        # contract still forbids predicting harm, prescribing remedies, or
        # frightening anyone, and `grounding.py` still checks the output.
        self._safety = [
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
            types.SafetySetting(
                category=types.HarmCategory.HARM_CATEGORY_HARASSMENT,
                threshold=types.HarmBlockThreshold.BLOCK_ONLY_HIGH,
            ),
        ]

    @staticmethod
    def _error_types() -> tuple[type[Exception], ...]:
        try:
            from google.genai import errors

            return (errors.APIError,)
        except Exception:  # pragma: no cover - SDK layout guard
            return (Exception,)

    def _contents(self, request: Request) -> list[Any]:
        """Translate provider-neutral messages into Gemini `Content` objects.

        Gemini names the assistant turn "model"; sending "assistant" is
        rejected, so the mapping happens here rather than leaking the provider's
        vocabulary into `interpret.py`.
        """
        types = self._types
        return [
            types.Content(
                role="model" if message["role"] == "assistant" else "user",
                parts=[types.Part(text=str(message["content"]))],
            )
            for message in request.messages
        ]

    @staticmethod
    def _thinking_for(model: str) -> str:
        """The thinking level this model will actually accept.

        Kept as a lookup rather than a try/catch so a fallback hop never spends
        a round trip discovering a 400 it could have predicted.
        """
        if THINKING_LEVEL == "MINIMAL" and model in _NO_MINIMAL:
            return "LOW"
        return THINKING_LEVEL

    def _config(self, request: Request, model: str) -> Any:
        types = self._types
        return types.GenerateContentConfig(
            system_instruction=_system_instruction(request.suffix),
            max_output_tokens=request.max_tokens,
            temperature=TEMPERATURE,
            safety_settings=self._safety,
            thinking_config=types.ThinkingConfig(
                thinking_level=self._thinking_for(model)
            ),
            # No tools are declared, so the SDK's automatic function calling
            # only adds a warning on every call.
            automatic_function_calling=types.AutomaticFunctionCallingConfig(
                disable=True
            ),
        )

    def _check(self, response: Any, *, streaming: bool = False) -> None:
        """Raise if the response was withheld rather than generated.

        A blocked prompt and a blocked completion surface differently — the
        first on `prompt_feedback`, the second as a candidate `finish_reason` —
        and neither raises on its own, so both are checked before the text is
        read.

        `streaming` relaxes the empty-candidates check: a stream's trailing
        chunk can carry usage metadata and nothing else, which is normal there
        and a failure in a single response.
        """
        feedback = getattr(response, "prompt_feedback", None)
        if feedback is not None and getattr(feedback, "block_reason", None):
            raise InterpretationBlocked(
                f"the request was blocked by a safety filter "
                f"({feedback.block_reason})"
            )

        candidates = getattr(response, "candidates", None) or []
        if not candidates:
            if streaming:
                return
            raise InterpretationUnavailable("the model returned no response")

        reason = getattr(candidates[0], "finish_reason", None)
        name = getattr(reason, "name", str(reason) if reason else "")
        if name in {"SAFETY", "PROHIBITED_CONTENT", "BLOCKLIST", "SPII"}:
            raise InterpretationBlocked(
                f"the response was withheld by a safety filter ({name})"
            )

        if name == "MAX_TOKENS":
            raise InterpretationTruncated(
                "the reading was cut off — raise ASTRO_MAX_TOKENS or lower "
                "ASTRO_THINKING_LEVEL"
            )

    @staticmethod
    def _is_capacity_error(exc: Exception) -> bool:
        """Whether another model is worth trying.

        Capacity and rate limiting are properties of one model at one moment; a
        bad request or a rejected key would fail identically everywhere, so
        those propagate immediately rather than burning the whole chain.
        """
        code = getattr(exc, "code", None) or getattr(exc, "status_code", None)
        if code in (429, 503):
            return True
        text = str(exc)
        return "UNAVAILABLE" in text or "RESOURCE_EXHAUSTED" in text

    def complete(self, request: Request) -> str:
        last: Exception | None = None

        for model in _model_chain():
            try:
                response = self._client.models.generate_content(
                    model=model,
                    contents=self._contents(request),
                    config=self._config(request, model),
                )
            except self._errors as exc:
                if self._is_capacity_error(exc):
                    last = exc
                    continue
                raise InterpretationUnavailable(str(exc)) from exc

            self._check(response)
            return (response.text or "").strip()

        raise InterpretationUnavailable(
            f"every model was unavailable ({', '.join(_model_chain())}): {last}"
        )

    def stream(self, request: Request) -> Iterator[str]:
        """Stream an answer, failing over only before the first token.

        Once text has reached the reader a different model cannot take over
        mid-sentence — it has not seen what was already said. So the chain is
        walked while opening the stream, and a failure after that point is
        reported rather than retried.
        """
        last: Exception | None = None

        for model in _model_chain():
            started = False
            try:
                chunks = self._client.models.generate_content_stream(
                    model=model,
                    contents=self._contents(request),
                    config=self._config(request, model),
                )
                for chunk in chunks:
                    # A filter can cut a stream off part-way, so every chunk is
                    # checked rather than only the first.
                    self._check(chunk, streaming=True)
                    if chunk.text:
                        started = True
                        yield chunk.text
                return
            except InterpretationUnavailable:
                raise
            except self._errors as exc:
                if not started and self._is_capacity_error(exc):
                    last = exc
                    continue
                raise InterpretationUnavailable(str(exc)) from exc

        raise InterpretationUnavailable(
            f"every model was unavailable ({', '.join(_model_chain())}): {last}"
        )


_client: MessageClient | None = None


def get_client() -> MessageClient:
    """The process-wide client, built on first use."""
    global _client
    if _client is None:
        _client = GeminiClient()
    return _client


def set_client(client: MessageClient | None) -> None:
    """Install a client explicitly. Tests use this to inject a stub."""
    global _client
    _client = client


def is_configured() -> bool:
    """Whether an interpretation request could plausibly succeed.

    Lets the API fail with a clear message at the edge instead of a stack trace
    from inside the SDK.
    """
    if _client is not None:
        return True
    return bool(
        os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    )

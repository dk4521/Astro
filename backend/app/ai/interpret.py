"""Turning a computed chart into language.

The flow is always the same shape: compute deterministically, render the result
as facts, hand those facts to the model with a question, check what comes back
against the chart. The model's only input about the person is the fact block —
it has no other channel through which a placement could enter the answer.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from dataclasses import dataclass, field

from ..astro import Chart, panchang_for, vimshottari
from . import grounding
from .client import Request, get_client
from .facts import build_brief
from .prompts import READING_REQUEST, language_directive


@dataclass(frozen=True, slots=True)
class Interpretation:
    """A generated reading, with the checks that were run on it."""

    text: str
    language: str
    model_grounded: bool
    contradictions: list[str] = field(default_factory=list)


@dataclass(frozen=True, slots=True)
class Turn:
    """One prior exchange, replayed to give the model conversational memory."""

    role: str  # "user" | "assistant"
    content: str


def _brief_for(chart: Chart, as_of: dt.datetime, levels: int = 3) -> str:
    return build_brief(
        chart=chart,
        panchang=panchang_for(chart),
        timeline=vimshottari(chart, levels=levels),
        as_of=as_of,
    )


def _build_request(
    chart: Chart,
    question: str,
    language: str,
    as_of: dt.datetime,
    history: list[Turn] | None = None,
) -> Request:
    """Assemble the model request.

    The chart brief leads the first user turn so that every later turn in a
    conversation shares it as a stable prefix. History follows, and the current
    question comes last.
    """
    brief = _brief_for(chart, as_of)
    messages: list[dict[str, object]] = []

    if history:
        messages.append({"role": "user", "content": f"{brief}\n\n{history[0].content}"})
        for turn in history[1:]:
            messages.append({"role": turn.role, "content": turn.content})
        messages.append({"role": "user", "content": question})
    else:
        messages.append({"role": "user", "content": f"{brief}\n\n{question}"})

    return Request(messages=messages, suffix=language_directive(language))


def _verify(text: str, chart: Chart, language: str) -> Interpretation:
    contradictions = grounding.check(text, chart)
    return Interpretation(
        text=text,
        language=language,
        model_grounded=not contradictions,
        contradictions=[str(c) for c in contradictions],
    )


def reading(
    chart: Chart,
    language: str = "hinglish",
    as_of: dt.datetime | None = None,
) -> Interpretation:
    """A first introduction to the chart, with no question asked."""
    moment = as_of or dt.datetime.now(dt.timezone.utc)
    request = _build_request(chart, READING_REQUEST, language, moment)
    return _verify(get_client().complete(request), chart, language)


def answer(
    chart: Chart,
    question: str,
    language: str = "hinglish",
    as_of: dt.datetime | None = None,
    history: list[Turn] | None = None,
) -> Interpretation:
    """Answer one question about the chart."""
    moment = as_of or dt.datetime.now(dt.timezone.utc)
    request = _build_request(chart, question, language, moment, history)
    return _verify(get_client().complete(request), chart, language)


def stream_answer(
    chart: Chart,
    question: str,
    language: str = "hinglish",
    as_of: dt.datetime | None = None,
    history: list[Turn] | None = None,
) -> Iterator[str]:
    """Stream an answer token by token.

    Grounding cannot gate a stream — text reaches the reader before there is a
    complete claim to check. Callers that need the verdict should run
    `grounding.check` on the accumulated text once the stream closes and
    surface the result then; `/v1/chat` does exactly that in its final event.
    """
    moment = as_of or dt.datetime.now(dt.timezone.utc)
    request = _build_request(chart, question, language, moment, history)
    yield from get_client().stream(request)

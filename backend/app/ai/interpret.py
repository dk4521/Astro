"""Turning a computed chart into language.

The flow is always the same shape: compute deterministically, render the result
as facts, hand those facts to the model with a question, check what comes back
against the chart. The model's only input about the person is the fact block —
it has no other channel through which a placement could enter the answer.

Every model call goes through `cache` first. The request is assembled before the
lookup rather than after, which is the point: the assembled request *is* the
key, so a cached answer can only ever be served to a request built from the same
facts, the same prompt and the same model. Grounding still runs on the way out,
even on a hit — the check is cheap, and a tightened grounding rule should be
applied to a stored answer rather than trusted because it passed once.

**An answer that failed grounding is never stored.** Caching is a bet that the
same request deserves the same reply, and that bet is off for a reply already
known to contradict the chart it describes: storing it would turn one bad
reading into the same bad reading all day, and cost nothing to avoid, since the
retry the reader gets instead is a request they were going to spend anyway.
"""

from __future__ import annotations

import datetime as dt
from collections.abc import Iterator
from dataclasses import dataclass, field

from ..astro import Chart, panchang_for, vimshottari
from . import cache, grounding
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
    #: True when this text came from the cache rather than the model. Reported
    #: as a response header so a slow first reading and an instant second one
    #: can be told apart from the outside.
    cached: bool = False


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


def _verify(text: str, chart: Chart, language: str, cached: bool = False) -> Interpretation:
    contradictions = grounding.check(text, chart)
    return Interpretation(
        text=text,
        language=language,
        model_grounded=not contradictions,
        contradictions=[str(c) for c in contradictions],
        cached=cached,
    )


def _complete(request: Request, chart: Chart, language: str) -> Interpretation:
    """One model call, or none at all if this exact request has been made."""
    stored = cache.get(request)
    if stored is not None:
        return _verify(stored, chart, language, cached=True)

    result = _verify(get_client().complete(request), chart, language)
    if result.model_grounded:
        cache.put(request, result.text)
    return result


def reading(
    chart: Chart,
    language: str = "hinglish",
    as_of: dt.datetime | None = None,
) -> Interpretation:
    """A first introduction to the chart, with no question asked."""
    moment = as_of or dt.datetime.now(dt.timezone.utc)
    request = _build_request(chart, READING_REQUEST, language, moment)
    return _complete(request, chart, language)


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
    return _complete(request, chart, language)


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

    A cached answer is yielded whole rather than re-chunked into a fake typing
    animation. Pretending to think about an answer we already have would be a
    small lie told by the UI, and the honest version is also the better one:
    asking the same question twice comes back instantly.
    """
    moment = as_of or dt.datetime.now(dt.timezone.utc)
    request = _build_request(chart, question, language, moment, history)

    stored = cache.get(request)
    if stored is not None:
        yield stored
        return

    collected: list[str] = []
    for chunk in get_client().stream(request):
        collected.append(chunk)
        yield chunk

    # Only a stream that ran to completion is worth storing. An answer cut short
    # by an error, or by the reader leaving the screen, would otherwise be
    # cached as if it were the whole thing — and served that way for a day.
    #
    # The grounding check here is a second one: `/v1/chat` runs its own to build
    # the terminal event. They answer different questions — that one is what the
    # reader is told, this one is whether the answer is fit to keep — and the
    # check is a scan over text the caller already holds.
    text = "".join(collected)
    if not grounding.check(text, chart):
        cache.put(request, text)

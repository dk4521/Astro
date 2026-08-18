"""Shape of a course chapter.

Content lives on the server, not in the bundle. Thirty chapters in two languages
is a few hundred kilobytes of prose; shipping it inside the app would inflate
every install for material most readers touch a chapter at a time. It also means
a typo, a clarification, or a whole new chapter ships without an app release —
which matters for teaching material that will be corrected far more often than
the code around it.

The prose is data, deliberately. Nothing here is generated: `Chapter` holds text
written by a person, and `personalise` holds a pure function of the reader's
computed chart. Neither path can reach a model, which is what makes this the one
part of the app that cannot hallucinate.
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Literal

Language = Literal["en", "hi"]
LANGUAGES: tuple[Language, ...] = ("en", "hi")

# A string in both languages. Hindi is not a translation afterthought here — most
# of this market reads it, and a course that exists only in English teaches the
# people who least need teaching.
Text = dict[str, str]


@dataclass(frozen=True, slots=True)
class Section:
    heading: Text
    body: tuple[Text, ...]
    # A short callout: a caution, or the confusion this section usually causes.
    aside: Text | None = None


@dataclass(frozen=True, slots=True)
class Chapter:
    slug: str
    part: Text
    title: Text
    summary: Text
    minutes: int
    level: Literal["basic", "intermediate"]
    sections: tuple[Section, ...]
    # Locates the chapter's idea in the reader's own chart. Receives the same
    # computed objects the chart screen draws; returns text per language, or
    # None when this chart has no example to point at — an honest gap rather
    # than an invented one.
    personalise: Callable[..., Text | None] | None = field(default=None, compare=False)


def pick(text: Text, language: str) -> str:
    """The requested language, falling back to English rather than to nothing."""
    return text.get(language) or text["en"]


def apply_personalisation(
    chapter: "Chapter", chart, panchang, dasha, place: str | None
) -> Text | None:
    """Run a chapter's personalisation, whatever arity it declared.

    Most of these need only the computed objects; a couple also want the display
    name of the birth place, which the engine does not carry. Reading the real
    signature keeps that optional without every function having to accept an
    argument it ignores.
    """
    if chapter.personalise is None:
        return None

    import inspect

    if "place" in inspect.signature(chapter.personalise).parameters:
        return chapter.personalise(chart, panchang, dasha, place)
    return chapter.personalise(chart, panchang, dasha)

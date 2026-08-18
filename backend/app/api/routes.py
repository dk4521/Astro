"""HTTP surface over the astrology engine.

Every endpoint here is a pure function of its request body. Nothing is stored,
nothing is random, and no model is called — which is what lets the whole API be
cached aggressively and lets a chart be reproduced from its inputs alone.

The two interpretation endpoints are the exception, and the only ones that cost
anything: they go through `ai.cache`, which reuses an answer when the exact same
request has already been made. `/v1/interpret` reports which it was in `X-Cache`,
so a slow first reading and an instant second one can be told apart from outside
the process.
"""

from __future__ import annotations

import datetime as dt
import json
from zoneinfo import ZoneInfo

from fastapi import APIRouter, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from .. import ai, course, places
from ..ai import grounding
from ..astro import build_chart, navamsa_chart, panchang_for, vimshottari
from ..astro.chart import Chart, Placement
from ..astro.dasha import DashaPeriod
from ..schemas import (
    BirthDetails,
    ChapterOut,
    ChapterRequest,
    ChartMeta,
    ChartResponse,
    ChatRequest,
    CourseEntryOut,
    CourseIndexOut,
    CourseSectionOut,
    DashaPeriodOut,
    DashaResponse,
    GrahaOut,
    InterpretRequest,
    InterpretResponse,
    PanchangResponse,
    PlaceOut,
    PlacementOut,
    ReadingResponse,
    TodayResponse,
)

router = APIRouter()


# --- Serialization ----------------------------------------------------------


def _placement_out(placement: Placement) -> PlacementOut:
    return PlacementOut(
        longitude=placement.longitude,
        rashi=placement.rashi,
        rashi_en=placement.rashi_en,
        rashi_lord=placement.rashi_lord,
        degree=placement.degree_in_rashi,
        degree_dms=placement.dms,
        nakshatra=placement.nakshatra,
        nakshatra_lord=placement.nakshatra_lord,
        pada=placement.pada,
        navamsa=placement.navamsa,
    )


def _chart_out(chart: Chart, place: str | None) -> ChartResponse:
    return ChartResponse(
        meta=ChartMeta(
            birth_local=chart.birth_local,
            birth_utc=chart.birth_utc,
            timezone=chart.timezone,
            latitude=chart.latitude,
            longitude=chart.longitude,
            place=place,
            julian_day=chart.julian_day,
            ayanamsa=chart.ayanamsa,
            ayanamsa_name=chart.ayanamsa_name,
            ephemeris_mode=chart.ephemeris_mode,
        ),
        lagna=_placement_out(chart.lagna),
        grahas=[
            GrahaOut(
                graha=g.graha,
                graha_hi=g.graha_hi,
                house=g.house,
                retrograde=g.retrograde,
                combust=g.combust,
                speed=g.speed,
                placement=_placement_out(g.placement),
            )
            for g in chart.grahas.values()
        ],
        houses=chart.houses,
        house_lords=chart.house_lords,
        navamsa=navamsa_chart(chart),
        moon_rashi=chart.moon_rashi,
        janma_nakshatra=chart.janma_nakshatra,
    )


def _period_out(period: DashaPeriod) -> DashaPeriodOut:
    return DashaPeriodOut(
        lord=period.lord,
        lord_hi=period.lord_hi,
        start=period.start,
        end=period.end,
        level=period.level,
        years=period.duration_years,
        children=[_period_out(child) for child in period.children],
    )


def _build(details: BirthDetails) -> Chart:
    """Cast a chart, turning engine validation errors into 422s."""
    try:
        return build_chart(
            details.local_datetime(),
            details.latitude,
            details.longitude,
            details.timezone,
        )
    except ValueError as exc:
        raise HTTPException(status_code=422, detail=str(exc)) from exc


def _panchang_out(chart: Chart) -> PanchangResponse:
    p = panchang_for(chart)
    return PanchangResponse(
        tithi=p.tithi,
        tithi_number=p.tithi_number,
        paksha=p.paksha,
        tithi_percent=p.tithi_percent,
        nakshatra=p.nakshatra,
        nakshatra_pada=p.nakshatra_pada,
        yoga=p.yoga,
        karana=p.karana,
        vara=p.vara,
        vara_lord=p.vara_lord,
    )


def _dasha_out(chart: Chart, levels: int, as_of: dt.datetime) -> DashaResponse:
    timeline = vimshottari(chart, levels=levels)
    return DashaResponse(
        janma_nakshatra=timeline.janma_nakshatra,
        janma_nakshatra_lord=timeline.janma_nakshatra_lord,
        balance_years=timeline.balance_years,
        as_of=as_of,
        active=[_period_out(p) for p in timeline.at(as_of)],
        periods=[_period_out(p) for p in timeline.periods],
    )


def _resolve_as_of(as_of: dt.datetime | None) -> dt.datetime:
    """Default to now, and treat a naive input as UTC."""
    if as_of is None:
        return dt.datetime.now(dt.timezone.utc)
    if as_of.tzinfo is None:
        return as_of.replace(tzinfo=dt.timezone.utc)
    return as_of


# --- Endpoints --------------------------------------------------------------


@router.post("/chart", response_model=ChartResponse, summary="Cast a natal chart")
def chart(details: BirthDetails) -> ChartResponse:
    return _chart_out(_build(details), details.place)


@router.post("/panchang", response_model=PanchangResponse, summary="Panchang at birth")
def panchang(details: BirthDetails) -> PanchangResponse:
    return _panchang_out(_build(details))


@router.post("/dasha", response_model=DashaResponse, summary="Vimshottari timeline")
def dasha(
    details: BirthDetails,
    levels: int = Query(default=2, ge=1, le=3, description="Nesting depth"),
    as_of: dt.datetime | None = Query(
        default=None, description="Moment to report active periods for; defaults to now"
    ),
) -> DashaResponse:
    return _dasha_out(_build(details), levels, _resolve_as_of(as_of))


@router.post(
    "/reading",
    response_model=ReadingResponse,
    summary="Everything deterministic about a nativity",
)
def reading(
    details: BirthDetails,
    levels: int = Query(default=2, ge=1, le=3),
    as_of: dt.datetime | None = Query(default=None),
) -> ReadingResponse:
    """The single call the mobile app makes on load.

    This is also the exact payload the interpretation layer will be handed —
    the AI translates this object into language and never computes any part of
    it, so hallucinated positions are structurally impossible.
    """
    built = _build(details)
    return ReadingResponse(
        chart=_chart_out(built, details.place),
        panchang=_panchang_out(built),
        dasha=_dasha_out(built, levels, _resolve_as_of(as_of)),
    )


# --- Interpretation ---------------------------------------------------------


def _require_interpreter() -> None:
    """Fail early and legibly when no model credentials are configured."""
    if not ai.is_configured():
        raise HTTPException(
            status_code=503,
            detail=(
                "Interpretation is not configured. Set GEMINI_API_KEY on the "
                "server (see backend/.env.example)."
            ),
        )


@router.post(
    "/interpret",
    response_model=InterpretResponse,
    summary="Explain a chart in plain language",
)
def interpret(payload: InterpretRequest, response: Response) -> InterpretResponse:
    """A first reading of the chart.

    Everything factual in the response was computed before the model saw it;
    the model's role is translation. The `grounded` flag reports whether the
    text it produced actually agrees with the chart.
    """
    _require_interpreter()
    chart = _build(payload.birth)

    try:
        result = ai.reading(chart, language=payload.language)
    except ai.InterpretationUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    response.headers["X-Cache"] = "hit" if result.cached else "miss"

    return InterpretResponse(
        text=result.text,
        language=payload.language,
        grounded=result.model_grounded,
        contradictions=result.contradictions,
    )


@router.post("/chat", summary="Ask a question about a chart (streamed)")
def chat(payload: ChatRequest) -> StreamingResponse:
    """Stream an answer as server-sent events.

    Events are `token` while generating, then exactly one terminal event:
    `done` carrying the grounding verdict, or `error`. The grounding check can
    only run on the complete text, so it arrives last rather than gating the
    stream — the client should surface a failed check after the fact.
    """
    _require_interpreter()
    chart = _build(payload.birth)
    history = [ai.Turn(role=t.role, content=t.content) for t in payload.history]

    def events():
        collected: list[str] = []
        try:
            for chunk in ai.stream_answer(
                chart,
                payload.question,
                language=payload.language,
                history=history,
            ):
                collected.append(chunk)
                yield f"event: token\ndata: {json.dumps({'text': chunk})}\n\n"
        except ai.InterpretationUnavailable as exc:
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"
            return

        text = "".join(collected)
        contradictions = [str(c) for c in grounding.check(text, chart)]
        payload_out = {
            "grounded": not contradictions,
            "contradictions": contradictions,
        }
        yield f"event: done\ndata: {json.dumps(payload_out)}\n\n"

    return StreamingResponse(
        events(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )


@router.get("/places", response_model=list[PlaceOut], summary="Search birth places")
def place_search(
    response: Response,
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PlaceOut]:
    # A gazetteer of populated places, shipped with the service. Cities do not
    # move, so this is as cacheable as a static file — and onboarding fires a
    # request every 250 ms while someone types a city name.
    response.headers["Cache-Control"] = "public, max-age=86400"
    return places.search(q, limit)


# --- Today ------------------------------------------------------------------


@router.post("/today", response_model=TodayResponse, summary="The sky now, and your period")
def today(details: BirthDetails) -> TodayResponse:
    """Panchang for this moment at the reader's place, plus their active dasha.

    Two charts are cast, not one: the natal chart, which the dasha timeline runs
    from, and a chart for *now* at the same coordinates, which is where today's
    panchang comes from. A panchang is a property of a moment and a place, and
    the reader's birth place is the only location the app knows.

    Deterministic all the way down — no model, no quota, no cost. That is the
    point: this is the screen a user can open several times a day.
    """
    natal = _build(details)

    now_utc = dt.datetime.now(dt.timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo(natal.timezone)).replace(tzinfo=None)
    sky = build_chart(now_local, details.latitude, details.longitude, natal.timezone)

    moon = sky.grahas["Moon"]
    sun = sky.grahas["Sun"]

    return TodayResponse(
        as_of=now_utc,
        timezone=natal.timezone,
        place=details.place,
        panchang=_panchang_out(sky),
        moon_rashi=moon.placement.rashi,
        moon_nakshatra=moon.placement.nakshatra,
        sun_rashi=sun.placement.rashi,
        active=[
            _period_out(p) for p in vimshottari(natal, levels=3).at(now_utc)
        ],
        birth_moon_rashi=natal.moon_rashi,
        birth_nakshatra=natal.janma_nakshatra,
    )


# --- Course -----------------------------------------------------------------
#
# Content lives here rather than in the app bundle: thirty chapters in two
# languages would inflate every install for material read a chapter at a time,
# and a correction to teaching material should not need an app release.


def _language(value: str) -> str:
    return value if value in course.LANGUAGES else "en"


@router.get("/course", response_model=CourseIndexOut, summary="Course index")
def course_index(
    response: Response,
    language: str = Query(default="en", description="en or hi"),
) -> CourseIndexOut:
    # Shorter than the gazetteer because chapter titles are edited: an hour is
    # long enough to spare the repeat fetches the Learn screen makes on every
    # visit, and short enough that a corrected typo appears the same morning.
    response.headers["Cache-Control"] = "public, max-age=3600"
    lang = _language(language)
    return CourseIndexOut(
        language=lang,
        chapters=[
            CourseEntryOut(
                slug=chapter.slug,
                number=number,
                part=course.pick(chapter.part, lang),
                title=course.pick(chapter.title, lang),
                summary=course.pick(chapter.summary, lang),
                minutes=chapter.minutes,
                level=chapter.level,
            )
            for number, chapter in enumerate(course.CHAPTERS, start=1)
        ],
        total_minutes=sum(c.minutes for c in course.CHAPTERS),
    )


@router.post("/course/{slug}", response_model=ChapterOut, summary="One chapter")
def course_chapter(
    slug: str,
    payload: ChapterRequest,
    language: str = Query(default="en", description="en or hi"),
) -> ChapterOut:
    """One chapter, optionally located in the reader's own chart.

    `in_your_chart` is computed by the engine from the birth details sent with
    the request — the same arithmetic the chart screen draws. No model is
    involved anywhere in this endpoint, which is why it cannot be wrong in the
    way generated text can be wrong.
    """
    chapter = course.CHAPTERS_BY_SLUG.get(slug)
    if chapter is None:
        raise HTTPException(status_code=404, detail=f"no chapter named {slug!r}")

    lang = _language(language)
    index = course.CHAPTERS.index(chapter)
    following = course.CHAPTERS[index + 1] if index + 1 < len(course.CHAPTERS) else None

    personalised: str | None = None
    if payload.birth is not None and chapter.personalise is not None:
        chart = _build(payload.birth)
        text = course.apply_personalisation(
            chapter,
            chart,
            panchang_for(chart),
            vimshottari(chart, levels=3),
            payload.birth.place,
        )
        if text is not None:
            personalised = course.pick(text, lang)

    return ChapterOut(
        slug=chapter.slug,
        number=index + 1,
        part=course.pick(chapter.part, lang),
        title=course.pick(chapter.title, lang),
        summary=course.pick(chapter.summary, lang),
        minutes=chapter.minutes,
        level=chapter.level,
        language=lang,
        sections=[
            CourseSectionOut(
                heading=course.pick(section.heading, lang),
                body=[course.pick(paragraph, lang) for paragraph in section.body],
                aside=course.pick(section.aside, lang) if section.aside else None,
            )
            for section in chapter.sections
        ],
        next_slug=following.slug if following else None,
        in_your_chart=personalised,
    )

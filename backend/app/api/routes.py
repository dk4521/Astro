"""HTTP surface over the astrology engine.

Every endpoint here is a pure function of its request body. Nothing is stored,
nothing is random, and no model is called — which is what lets the whole API be
cached aggressively and lets a chart be reproduced from its inputs alone.
"""

from __future__ import annotations

import datetime as dt
import json

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from .. import ai, places
from ..ai import grounding
from ..astro import build_chart, navamsa_chart, panchang_for, vimshottari
from ..astro.chart import Chart, Placement
from ..astro.dasha import DashaPeriod
from ..schemas import (
    BirthDetails,
    ChartMeta,
    ChartResponse,
    ChatRequest,
    DashaPeriodOut,
    DashaResponse,
    GrahaOut,
    InterpretRequest,
    InterpretResponse,
    PanchangResponse,
    PlaceOut,
    PlacementOut,
    ReadingResponse,
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
def interpret(payload: InterpretRequest) -> InterpretResponse:
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
    q: str = Query(min_length=1, max_length=100),
    limit: int = Query(default=10, ge=1, le=50),
) -> list[PlaceOut]:
    return places.search(q, limit)

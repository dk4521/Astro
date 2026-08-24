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
import uuid
from zoneinfo import ZoneInfo

from fastapi import APIRouter, Depends, HTTPException, Query, Response
from fastapi.responses import StreamingResponse

from .. import ai, auth, course, meanings, places, tarot
from ..billing import store
from ..ai import grounding
from ..tarot import reading as tarot_reading
from ..astro import ashtakoot, build_chart, navamsa_chart, panchang_for, vimshottari
from ..astro.ephemeris import from_julian_day
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
    KootOut,
    MatchRequest,
    MatchResponse,
    PanchangResponse,
    PlaceOut,
    PlacementOut,
    ReadingResponse,
    TarotCardOut,
    TarotDeckResponse,
    TarotDrawnOut,
    TarotDrawRequest,
    TarotDrawResponse,
    TarotPositionOut,
    TarotReadingRequest,
    TarotReadingResponse,
    TarotSuitOut,
    TipRequest,
    TipResponse,
    TodayResponse,
)

router = APIRouter()


# --- Serialization ----------------------------------------------------------


def _placement_out(placement: Placement) -> PlacementOut:
    return PlacementOut(
        longitude=placement.longitude,
        rashi=placement.rashi,
        rashi_en=placement.rashi_en,
        rashi_hi=placement.rashi_hi,
        rashi_lord=placement.rashi_lord,
        rashi_lord_hi=placement.rashi_lord_hi,
        degree=placement.degree_in_rashi,
        degree_dms=placement.dms,
        nakshatra=placement.nakshatra,
        nakshatra_hi=placement.nakshatra_hi,
        nakshatra_lord=placement.nakshatra_lord,
        nakshatra_lord_hi=placement.nakshatra_lord_hi,
        pada=placement.pada,
        navamsa=placement.navamsa,
        navamsa_hi=placement.navamsa_hi,
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
            ayanamsa_name_hi=chart.ayanamsa_name_hi,
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
        moon_rashi_hi=chart.moon_rashi_hi,
        janma_nakshatra=chart.janma_nakshatra,
        janma_nakshatra_hi=chart.janma_nakshatra_hi,
    )


def _period_out(period: DashaPeriod, *, with_meaning: bool = False) -> DashaPeriodOut:
    return DashaPeriodOut(
        lord=period.lord,
        lord_hi=period.lord_hi,
        start=period.start,
        end=period.end,
        level=period.level,
        years=period.duration_years,
        children=[_period_out(child) for child in period.children],
        meaning=meanings.dasha_meaning(period.lord, "en") if with_meaning else None,
        meaning_hi=meanings.dasha_meaning(period.lord, "hi") if with_meaning else None,
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


def _moment(jd: float | None) -> dt.datetime | None:
    """A Julian day as a UTC instant, or None passed straight through."""
    return None if jd is None else from_julian_day(jd)


def _panchang_out(chart: Chart) -> PanchangResponse:
    p = panchang_for(chart)
    return PanchangResponse(
        tithi=p.tithi,
        tithi_hi=p.tithi_hi,
        tithi_number=p.tithi_number,
        paksha=p.paksha,
        paksha_hi=p.paksha_hi,
        tithi_percent=p.tithi_percent,
        nakshatra=p.nakshatra,
        nakshatra_hi=p.nakshatra_hi,
        nakshatra_pada=p.nakshatra_pada,
        yoga=p.yoga,
        yoga_hi=p.yoga_hi,
        karana=p.karana,
        karana_hi=p.karana_hi,
        vara=p.vara,
        vara_hi=p.vara_hi,
        vara_lord=p.vara_lord,
        vara_lord_hi=p.vara_lord_hi,
        masa=p.masa,
        masa_hi=p.masa_hi,
        vikram_samvat=p.vikram_samvat,
        shaka_samvat=p.shaka_samvat,
        sunrise=_moment(p.sunrise_jd),
        sunset=_moment(p.sunset_jd),
        moonrise=_moment(p.moonrise_jd),
        moonset=_moment(p.moonset_jd),
    )


def _dasha_out(chart: Chart, levels: int, as_of: dt.datetime) -> DashaResponse:
    timeline = vimshottari(chart, levels=levels)
    return DashaResponse(
        janma_nakshatra=timeline.janma_nakshatra,
        janma_nakshatra_lord=timeline.janma_nakshatra_lord,
        balance_years=timeline.balance_years,
        as_of=as_of,
        active=[_period_out(p, with_meaning=True) for p in timeline.at(as_of)],
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


@router.post("/match", response_model=MatchResponse, summary="Ashtakoot Milan")
def match(payload: MatchRequest) -> MatchResponse:
    """The eight koots for two nativities.

    Deterministic, like everything else on this side of the app: no model, no
    quota, and the same two birth times give the same eight numbers forever.

    What it deliberately does not return is a verdict. There is no threshold
    here, no label, no "compatible" — because a score out of 36 is not a fact
    about two people, and turning it into one is the use of this procedure the
    course refuses to endorse. The caller gets the arithmetic and the values it
    came from; what to make of it is not the server's to say.
    """
    bride = _build(payload.bride)
    groom = _build(payload.groom)

    bride_moon = bride.grahas["Moon"].placement
    groom_moon = groom.grahas["Moon"].placement

    result = ashtakoot(
        bride_moon.nakshatra_index,
        bride_moon.rashi_index,
        groom_moon.nakshatra_index,
        groom_moon.rashi_index,
    )

    return MatchResponse(
        koots=[
            KootOut(
                name=k.name,
                points=k.points,
                maximum=k.maximum,
                bride=k.bride,
                bride_hi=k.bride_hi,
                groom=k.groom,
                groom_hi=k.groom_hi,
            )
            for k in result.koots
        ],
        total=result.total,
        maximum=result.maximum,
        bride_nakshatra=bride_moon.nakshatra,
        bride_nakshatra_hi=bride_moon.nakshatra_hi,
        bride_rashi=bride_moon.rashi,
        bride_rashi_hi=bride_moon.rashi_hi,
        groom_nakshatra=groom_moon.nakshatra,
        groom_nakshatra_hi=groom_moon.nakshatra_hi,
        groom_rashi=groom_moon.rashi,
        groom_rashi_hi=groom_moon.rashi_hi,
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


@router.post("/tip", response_model=TipResponse, summary="One line for the home screen")
def tip(payload: TipRequest, response: Response) -> TipResponse:
    """The daily line the app opens with.

    Two charts again, as in `/today`: the natal one the dasha runs from, and one
    for this moment at the same place, which is where the day comes from.

    This is the most expensive endpoint in the product, not per call but per
    user: it is the first thing the app shows, so without caching on both sides
    a single launch would spend one of the twenty daily requests. `X-Cache` says
    which it was, and the client caches for the day on top of this.
    """
    _require_interpreter()
    natal = _build(payload.birth)

    now_utc = dt.datetime.now(dt.timezone.utc)
    now_local = now_utc.astimezone(ZoneInfo(natal.timezone)).replace(tzinfo=None)
    sky = build_chart(now_local, payload.birth.latitude, payload.birth.longitude, natal.timezone)

    try:
        result = ai.daily_tip(
            natal, sky, language=payload.language, companion=payload.companion
        )
    except ai.InterpretationUnavailable as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    response.headers["X-Cache"] = "hit" if result.cached else "miss"

    return TipResponse(
        text=result.text,
        language=payload.language,
        companion=payload.companion,
        grounded=result.model_grounded,
    )


def _charge(account: auth.Account | None, request_id: str | None) -> tuple[str | None, str, int]:
    """Take the credit this message costs, before a single token is generated.

    Returns (account id charged, the reference it was charged under, balance
    left). The first is None on a deployment with no Supabase project, where
    billing does not exist and the endpoint behaves as it always did — that is
    what lets the engine be run locally without standing up payments.

    Two failures, told apart on purpose. Not signed in is 401 and means "sign
    in"; signed in with nothing left is 402 and means "top up". A single status
    for both would leave the app guessing which screen to show.
    """
    if not store.is_configured():
        return None, "", 0

    if account is None:
        raise HTTPException(status_code=401, detail="Sign in to ask a question.")

    ref = request_id or str(uuid.uuid4())

    try:
        allowed, balance = store.consume_credit(account.id, ref)
    except store.StoreError as exc:
        # Falling open here would make the paywall optional for anyone who can
        # cause a timeout, so it closes — and says so honestly rather than
        # claiming the credits ran out.
        raise HTTPException(
            status_code=503, detail="Could not check your balance just now. Try again."
        ) from exc

    if not allowed:
        raise HTTPException(
            status_code=402,
            detail="You have used all your messages. Top up or wait for tomorrow's.",
        )

    return account.id, ref, balance


@router.post("/chat", summary="Ask a question about a chart (streamed)")
def chat(
    payload: ChatRequest,
    account: auth.Account | None = Depends(auth.optional_user),
) -> StreamingResponse:
    """Stream an answer as server-sent events.

    Events are `token` while generating, then exactly one terminal event:
    `done` carrying the grounding verdict and the balance left, or `error`. The
    grounding check can only run on the complete text, so it arrives last
    rather than gating the stream — the client should surface a failed check
    after the fact.

    The credit is taken before the generator starts, not inside it. A
    `StreamingResponse` has already sent 200 by the time its body runs, so a
    refusal raised in there would arrive as an `error` event on a successful
    response rather than as the 402 the app needs to act on.
    """
    _require_interpreter()
    chart = _build(payload.birth)
    history = [ai.Turn(role=t.role, content=t.content) for t in payload.history]

    charged_to, ref, balance = _charge(account, payload.request_id)

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
            # Nothing was said, so nothing was spent. Capacity on the model
            # side is our problem, and charging for it would make a bad day for
            # the service into a bad day for the person paying.
            if charged_to and not collected:
                try:
                    store.refund_credit(charged_to, ref)
                except store.StoreError:
                    pass  # Logged upstream; a failed refund must not eat the error.
            yield f"event: error\ndata: {json.dumps({'detail': str(exc)})}\n\n"
            return

        text = "".join(collected)
        contradictions = [str(c) for c in grounding.check(text, chart)]
        payload_out = {
            "grounded": not contradictions,
            "contradictions": contradictions,
            "balance": balance,
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
        moon_rashi_hi=moon.placement.rashi_hi,
        moon_nakshatra=moon.placement.nakshatra,
        moon_nakshatra_hi=moon.placement.nakshatra_hi,
        sun_rashi=sun.placement.rashi,
        sun_rashi_hi=sun.placement.rashi_hi,
        active=[
            _period_out(p, with_meaning=True)
            for p in vimshottari(natal, levels=3).at(now_utc)
        ],
        birth_moon_rashi=natal.moon_rashi,
        birth_moon_rashi_hi=natal.moon_rashi_hi,
        birth_nakshatra=natal.janma_nakshatra,
        birth_nakshatra_hi=natal.janma_nakshatra_hi,
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


# --- Tarot ------------------------------------------------------------------
#
# The one place in this API where something is genuinely random, and it is
# handled the way the rest of the product handles everything: by making it
# reproducible. A draw returns the seed it was dealt from, and the same seed
# deals the same hand forever — so a spread can be shared, re-opened tomorrow,
# or checked, exactly like a chart can.
#
# Two of the three endpoints cost nothing and call no model. The written meaning
# of a card does not vary by reader and does not change tomorrow, so it is text
# a person wrote rather than text a model is asked for on every draw.


def _tarot_card_out(card: tarot.Card) -> TarotCardOut:
    return TarotCardOut(
        id=card.id,
        arcana=card.arcana,
        suit=card.suit,
        number=card.number,
        name=card.name["en"],
        name_hi=card.name["hi"],
        keywords=card.keywords["en"],
        keywords_hi=card.keywords["hi"],
        upright=card.upright["en"],
        upright_hi=card.upright["hi"],
        reversed=card.reversed["en"],
        reversed_hi=card.reversed["hi"],
    )


def _tarot_position_out(position: tarot.Position) -> TarotPositionOut:
    return TarotPositionOut(
        id=position.id,
        name=position.name["en"],
        name_hi=position.name["hi"],
        prompt=position.prompt["en"],
        prompt_hi=position.prompt["hi"],
    )


def _tarot_draw_out(drawn: tarot.Draw) -> TarotDrawResponse:
    return TarotDrawResponse(
        seed=drawn.seed,
        spread=tarot.SPREAD_NAME["en"],
        spread_hi=tarot.SPREAD_NAME["hi"],
        note=tarot.SPREAD_NOTE["en"],
        note_hi=tarot.SPREAD_NOTE["hi"],
        cards=[
            TarotDrawnOut(
                position=_tarot_position_out(item.position),
                card=_tarot_card_out(item.card),
                reversed=item.reversed,
                meaning=item.meaning("en"),
                meaning_hi=item.meaning("hi"),
            )
            for item in drawn.cards
        ],
    )


@router.get("/tarot/deck", response_model=TarotDeckResponse, summary="All 78 cards")
def tarot_deck(response: Response) -> TarotDeckResponse:
    """The written deck, in both languages.

    Cached for the same span as the course index and for the same reason: card
    meanings are prose, prose gets corrected, and a corrected line should reach
    readers the same morning rather than at the next app release.
    """
    response.headers["Cache-Control"] = "public, max-age=3600"
    return TarotDeckResponse(
        suits=[
            TarotSuitOut(
                id=suit.id,
                name=suit.name["en"],
                name_hi=suit.name["hi"],
                theme=suit.theme["en"],
                theme_hi=suit.theme["hi"],
            )
            for suit in tarot.SUITS
        ],
        cards=[_tarot_card_out(card) for card in tarot.CARDS],
    )


@router.post("/tarot/draw", response_model=TarotDrawResponse, summary="Deal three cards")
def tarot_draw(payload: TarotDrawRequest) -> TarotDrawResponse:
    """Situation, obstacle, advice — and the seed they came from.

    Free, and no model is involved: the cards are dealt by a seeded shuffle and
    every line returned with them was written by a person. Nobody should have to
    spend anything to turn three cards over.
    """
    return _tarot_draw_out(tarot.draw(payload.seed))


@router.post(
    "/tarot/reading",
    response_model=TarotReadingResponse,
    summary="Read the three cards together (costs a credit)",
)
def tarot_reading_endpoint(
    payload: TarotReadingRequest,
    account: auth.Account | None = Depends(auth.optional_user),
) -> TarotReadingResponse:
    """One reading of a spread, in the reader's language.

    The cards are re-dealt here from the seed rather than accepted from the
    client. That is what makes the charge honest in both directions: the reader
    pays for a reading of the hand the server itself dealt, and a modified app
    cannot assemble a flattering spread and buy words for it.

    Charged before the model is called, and refunded if the model never answers.
    Capacity on the provider's side is our problem, not the reader's.
    """
    _require_interpreter()

    drawn = tarot.draw(payload.seed)
    charged_to, ref, balance = _charge(account, payload.request_id)

    try:
        result = tarot_reading.interpret(
            drawn, question=payload.question, language=payload.language
        )
    except ai.InterpretationUnavailable as exc:
        if charged_to:
            try:
                store.refund_credit(charged_to, ref)
            except store.StoreError:
                pass  # Logged upstream; a failed refund must not eat the error.
        raise HTTPException(status_code=502, detail=str(exc)) from exc

    return TarotReadingResponse(
        seed=drawn.seed,
        text=result.text,
        language=payload.language,
        grounded=result.model_grounded,
        contradictions=result.contradictions,
        balance=balance if charged_to else None,
    )

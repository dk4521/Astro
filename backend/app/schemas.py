"""Request and response models for the public API.

These are deliberately separate from the engine's dataclasses: the engine is
free to grow internal detail without changing the contract the mobile app codes
against.
"""

from __future__ import annotations

import datetime as dt
from typing import Literal

from pydantic import BaseModel, ConfigDict, Field, field_validator


class BirthDetails(BaseModel):
    """Everything needed to cast a chart."""

    model_config = ConfigDict(
        json_schema_extra={
            "example": {
                "date": "1995-03-14",
                "time": "07:42",
                "latitude": 28.6139,
                "longitude": 77.2090,
                "place": "New Delhi, India",
            }
        }
    )

    date: dt.date = Field(description="Birth date in the local calendar")
    time: dt.time = Field(description="Local clock time at the birth place")
    latitude: float = Field(ge=-90.0, le=90.0)
    longitude: float = Field(ge=-180.0, le=180.0)
    place: str | None = Field(
        default=None, max_length=200, description="Display label only"
    )
    timezone: str | None = Field(
        default=None,
        max_length=64,
        description=(
            "IANA timezone override. Omit to resolve from the coordinates, "
            "which is correct for essentially every real birth place."
        ),
    )

    @field_validator("timezone")
    @classmethod
    def _known_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None
        from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

        try:
            ZoneInfo(value)
        except (ZoneInfoNotFoundError, ValueError) as exc:
            raise ValueError(f"unknown IANA timezone: {value!r}") from exc
        return value

    def local_datetime(self) -> dt.datetime:
        return dt.datetime.combine(self.date, self.time)


# Every Devanagari field below is sent alongside its Latin twin rather than
# instead of it: the app switches language without refetching, and a reading in
# one language must never have to guess the other.
class PlacementOut(BaseModel):
    longitude: float
    rashi: str
    rashi_en: str
    rashi_hi: str
    rashi_lord: str
    rashi_lord_hi: str
    degree: float
    degree_dms: str
    nakshatra: str
    nakshatra_hi: str
    nakshatra_lord: str
    nakshatra_lord_hi: str
    pada: int
    navamsa: str
    navamsa_hi: str


class GrahaOut(BaseModel):
    graha: str
    graha_hi: str
    house: int
    retrograde: bool
    combust: bool
    speed: float
    placement: PlacementOut


class ChartMeta(BaseModel):
    """Provenance for the numbers — what produced them, and how."""

    birth_local: dt.datetime
    birth_utc: dt.datetime
    timezone: str
    latitude: float
    longitude: float
    place: str | None
    julian_day: float
    ayanamsa: float
    ayanamsa_name: str
    ayanamsa_name_hi: str
    ephemeris_mode: str
    house_system: str = "whole-sign"


class ChartResponse(BaseModel):
    meta: ChartMeta
    lagna: PlacementOut
    grahas: list[GrahaOut]
    houses: dict[int, str]
    house_lords: dict[int, str]
    navamsa: dict[str, str]
    moon_rashi: str
    moon_rashi_hi: str
    janma_nakshatra: str
    janma_nakshatra_hi: str


class PanchangResponse(BaseModel):
    tithi: str
    tithi_hi: str
    tithi_number: int
    paksha: str
    paksha_hi: str
    tithi_percent: float
    nakshatra: str
    nakshatra_hi: str
    nakshatra_pada: int
    yoga: str
    yoga_hi: str
    karana: str
    karana_hi: str
    vara: str
    vara_hi: str
    vara_lord: str
    vara_lord_hi: str

    # The lunar month and the era year it turns with.
    masa: str
    masa_hi: str
    vikram_samvat: int = Field(
        description="Chaitradi (North Indian) reckoning: the year turns at Chaitra Shukla Pratipada"
    )
    shaka_samvat: int

    # Rise and set for the civil day at this place. Null is a real answer: the
    # Moon skips a rise once a month, and the polar Sun skips both for months.
    sunrise: dt.datetime | None = None
    sunset: dt.datetime | None = None
    moonrise: dt.datetime | None = None
    moonset: dt.datetime | None = None


class DashaPeriodOut(BaseModel):
    """One Vimshottari period.

    `meaning` is filled only for the periods actually running now. A full
    timeline at three levels is several hundred periods, and a written theme
    repeated against every one of them would be a hundred kilobytes of the same
    nine sentences — so the endpoints attach it where a screen displays it.
    """

    lord: str
    lord_hi: str
    start: dt.datetime
    end: dt.datetime
    level: int
    years: float
    children: list["DashaPeriodOut"] = Field(default_factory=list)
    meaning: str | None = None
    meaning_hi: str | None = None


class DashaResponse(BaseModel):
    janma_nakshatra: str
    janma_nakshatra_lord: str
    balance_years: float
    as_of: dt.datetime
    active: list[DashaPeriodOut] = Field(
        description="Nested periods running at `as_of`, outermost first"
    )
    periods: list[DashaPeriodOut]


class ReadingResponse(BaseModel):
    """The full deterministic payload the interpretation layer consumes.

    The AI layer is a translator of this object and never a source of it, so
    everything an interpretation could rest on has to be present here.
    """

    chart: ChartResponse
    panchang: PanchangResponse
    dasha: DashaResponse


Language = Literal["en", "hi", "hinglish"]


class InterpretRequest(BaseModel):
    """Ask for a first reading of a chart."""

    birth: BirthDetails
    language: Language = Field(
        default="hinglish",
        description="Hinglish is the default because it is how the target users talk",
    )


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str = Field(min_length=1, max_length=8000)


class ChatRequest(BaseModel):
    """Ask a question about a chart."""

    birth: BirthDetails
    question: str = Field(min_length=1, max_length=2000)
    language: Language = "hinglish"
    history: list[ChatTurn] = Field(
        default_factory=list,
        max_length=40,
        description="Prior turns, oldest first. The chart is re-sent each request.",
    )
    request_id: str | None = Field(
        default=None,
        max_length=64,
        description=(
            "Idempotency key for the credit this message costs. Send the same "
            "value when retrying a question whose stream died, and it is "
            "charged once. A new question needs a new value."
        ),
    )


class InterpretResponse(BaseModel):
    text: str
    language: Language
    grounded: bool = Field(
        description=(
            "False when the text contradicts the computed chart. Checked after "
            "generation, not requested of the model."
        )
    )
    contradictions: list[str] = Field(
        default_factory=list,
        description="Statements that disagree with the chart; empty when grounded",
    )


class KootOut(BaseModel):
    """One of the eight, with the values behind it.

    `bride` and `groom` are what each side actually contributed — the varna, the
    animal, the gana. They are sent so the screen can show *why* a koot scored
    what it did: a bare number out of 36 is the form of this procedure that gets
    used against people.
    """

    name: str
    points: float
    maximum: float
    bride: str
    bride_hi: str
    groom: str
    groom_hi: str


class MatchRequest(BaseModel):
    """Two nativities, in the roles the procedure names.

    The tradition's own split, kept rather than smoothed: Varna and Gana score
    differently if the two are swapped, so a symmetric API would be lying about
    what it computed.
    """

    bride: BirthDetails
    groom: BirthDetails


class MatchResponse(BaseModel):
    koots: list[KootOut]
    total: float
    maximum: float

    bride_nakshatra: str
    bride_nakshatra_hi: str
    bride_rashi: str
    bride_rashi_hi: str
    groom_nakshatra: str
    groom_nakshatra_hi: str
    groom_rashi: str
    groom_rashi_hi: str


class TipRequest(BaseModel):
    """Ask for the home screen's daily line."""

    birth: BirthDetails
    language: Language = "hinglish"
    companion: str | None = Field(
        default=None,
        max_length=40,
        description="Display name of the chat companion, so the line is in their voice",
    )


class TipResponse(BaseModel):
    text: str
    language: Language
    companion: str | None = None
    grounded: bool = Field(
        description="False when the line named a placement it was told not to name"
    )


class PlaceOut(BaseModel):
    name: str
    admin: str
    country: str
    latitude: float
    longitude: float

    @property
    def label(self) -> str:
        return f"{self.name}, {self.admin}"


# --- Course -----------------------------------------------------------------


class CourseEntryOut(BaseModel):
    """One row of the course index. Deliberately small: the index is fetched on
    every visit to the Learn screen, the chapters are not."""

    slug: str
    number: int
    part: str
    title: str
    summary: str
    minutes: int
    level: Literal["basic", "intermediate"]


class CourseIndexOut(BaseModel):
    language: str
    chapters: list[CourseEntryOut]
    total_minutes: int


class CourseSectionOut(BaseModel):
    heading: str
    body: list[str]
    aside: str | None = None


class ChapterOut(BaseModel):
    slug: str
    number: int
    part: str
    title: str
    summary: str
    minutes: int
    level: Literal["basic", "intermediate"]
    language: str
    sections: list[CourseSectionOut]
    next_slug: str | None = None
    in_your_chart: str | None = Field(
        default=None,
        description=(
            "The chapter's idea located in the requested chart, computed by the "
            "engine. Null when no birth details were sent, or when this chart "
            "has no example of the idea — an honest gap, never an invented one."
        ),
    )


class ChapterRequest(BaseModel):
    """Birth details are optional: the chapter reads without them, it is only
    the personalised line that needs a chart."""

    birth: BirthDetails | None = None


# --- Today ------------------------------------------------------------------


class TodayResponse(BaseModel):
    """The sky right now, plus where the reader is in their own timeline.

    Entirely deterministic — no model, no cost, no quota. That is what makes it
    safe to open several times a day.
    """

    as_of: dt.datetime
    timezone: str
    place: str | None
    panchang: PanchangResponse
    moon_rashi: str
    moon_rashi_hi: str
    moon_nakshatra: str
    moon_nakshatra_hi: str
    sun_rashi: str
    sun_rashi_hi: str
    active: list[DashaPeriodOut]
    birth_moon_rashi: str
    birth_moon_rashi_hi: str
    birth_nakshatra: str
    birth_nakshatra_hi: str


# --- Tarot ------------------------------------------------------------------
#
# Both languages travel together here, as they do for every computed value in
# this API: the app switches script without a refetch, and a deck downloaded in
# English must not have to be downloaded again in Hindi. Which is also why the
# deck and the draw take no `language` parameter at all — only the generated
# reading does, because that one really is written in one language.


class TarotCardOut(BaseModel):
    """One card. `arcana`, `suit` and `number` are drawing instructions too:
    the app has no card art and paints each face from these three."""

    id: str
    arcana: Literal["major", "minor"]
    suit: str | None
    number: int = Field(description="0–21 for the major arcana; 1–14 within a suit")
    name: str
    name_hi: str
    keywords: str
    keywords_hi: str
    upright: str
    upright_hi: str
    reversed: str
    reversed_hi: str


class TarotSuitOut(BaseModel):
    id: str
    name: str
    name_hi: str
    theme: str
    theme_hi: str


class TarotDeckResponse(BaseModel):
    """The whole deck. Static, written by a person, and cacheable as such."""

    suits: list[TarotSuitOut]
    cards: list[TarotCardOut]


class TarotPositionOut(BaseModel):
    id: str
    name: str
    name_hi: str
    prompt: str
    prompt_hi: str


class TarotDrawnOut(BaseModel):
    position: TarotPositionOut
    card: TarotCardOut
    reversed: bool
    meaning: str = Field(description="The written line for the way it actually came up")
    meaning_hi: str


class TarotDrawRequest(BaseModel):
    """Deal three cards.

    `seed` is the entire shuffle. Omit it for a fresh one; send a previous
    response's seed to deal that exact hand again, on any machine, any time.
    """

    seed: str | None = Field(
        default=None,
        pattern=r"^[A-Za-z0-9_-]{1,64}$",
        description="A previous draw's seed, to reproduce it",
    )


class TarotDrawResponse(BaseModel):
    seed: str
    spread: str
    spread_hi: str
    note: str
    note_hi: str
    cards: list[TarotDrawnOut]


class TarotReadingRequest(BaseModel):
    """Ask for the three cards to be read.

    The cards are not in this payload, and that is the point: the server deals
    them again from the seed. A client cannot buy a reading of a hand it made up.
    """

    seed: str = Field(pattern=r"^[A-Za-z0-9_-]{1,64}$")
    question: str | None = Field(default=None, max_length=2000)
    language: Language = "hinglish"
    request_id: str | None = Field(
        default=None,
        max_length=64,
        description=(
            "Idempotency key for the credit this reading costs. The same value "
            "twice is charged once, so a reading whose request failed can be "
            "retried without paying again."
        ),
    )


class TarotReadingResponse(BaseModel):
    seed: str
    text: str
    language: Language
    grounded: bool = Field(
        description=(
            "False when the reading named a card that was not dealt, or reached "
            "for astrology in a reply that was told there is no chart here."
        )
    )
    contradictions: list[str] = Field(default_factory=list)
    balance: int | None = Field(
        default=None, description="Credits left. Null where billing is not configured."
    )

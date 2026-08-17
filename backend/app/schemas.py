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


class PlacementOut(BaseModel):
    longitude: float
    rashi: str
    rashi_en: str
    rashi_lord: str
    degree: float
    degree_dms: str
    nakshatra: str
    nakshatra_lord: str
    pada: int
    navamsa: str


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
    janma_nakshatra: str


class PanchangResponse(BaseModel):
    tithi: str
    tithi_number: int
    paksha: str
    tithi_percent: float
    nakshatra: str
    nakshatra_pada: int
    yoga: str
    karana: str
    vara: str
    vara_lord: str


class DashaPeriodOut(BaseModel):
    lord: str
    lord_hi: str
    start: dt.datetime
    end: dt.datetime
    level: int
    years: float
    children: list["DashaPeriodOut"] = Field(default_factory=list)


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


class PlaceOut(BaseModel):
    name: str
    admin: str
    country: str
    latitude: float
    longitude: float

    @property
    def label(self) -> str:
        return f"{self.name}, {self.admin}"

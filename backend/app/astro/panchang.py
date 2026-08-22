"""Panchang: the five limbs of the Vedic calendar for a given moment.

Tithi, karana and yoga are all simple functions of the Sun-Moon relationship.
Tithi and karana use the *difference* of the two longitudes, so the ayanamsa
cancels and they are identical in tropical or sidereal terms. Yoga uses the
*sum*, where it does not cancel — so yoga must be computed sidereally, as it is
here.

Beyond the five limbs this also carries what a printed panchang puts at the top
of the page: the lunar month, the era year, and the four rise and set times. All
of them are properties of a moment *and a place* — which is why they come off a
Chart rather than off a timestamp.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass
from zoneinfo import ZoneInfo

from . import constants as K
from . import ephemeris as E
from .chart import Chart, decompose

TITHI_ARC = 12.0            # 360 / 30
KARANA_ARC = 6.0            # half a tithi
YOGA_ARC = 360.0 / 27.0

# 7 movable karanas cycle 8 times through tithi-halves 1..56, bracketed by 4
# fixed karanas: Kimstughna at the start, then Shakuni, Chatushpada, Naga.
_MOVABLE_KARANAS = (
    "Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti",
)
_FIXED_KARANAS = ("Kimstughna", "Shakuni", "Chatushpada", "Naga")


def _karana_name(index: int) -> str:
    """Name of karana `index` (0-59) within the lunar month."""
    if index == 0:
        return _FIXED_KARANAS[0]
    if index >= 57:
        return _FIXED_KARANAS[index - 56]
    return _MOVABLE_KARANAS[(index - 1) % 7]


@dataclass(frozen=True, slots=True)
class Panchang:
    """The five limbs, plus the values they were derived from."""

    tithi_index: int          # 0-29 across the full lunar month
    tithi: str
    tithi_number: int         # 1-15 within the paksha
    paksha: str               # Shukla or Krishna
    tithi_percent: float      # completion of the current tithi, 0-100

    nakshatra_index: int
    nakshatra: str            # the Moon's, i.e. janma nakshatra
    nakshatra_pada: int

    yoga_index: int
    yoga: str

    karana_index: int
    karana: str

    vara_index: int           # 0 = Ravivara
    vara: str
    vara_lord: str

    # The lunar month, and the two era years that turn with it.
    masa_index: int           # 0 = Chaitra
    masa: str
    vikram_samvat: int
    shaka_samvat: int

    # Julian days, UT. Any of them may be None and that is a real answer, not a
    # failure — see `ephemeris.rise_set`.
    sunrise_jd: float | None
    sunset_jd: float | None
    moonrise_jd: float | None
    moonset_jd: float | None

    sun_longitude: float
    moon_longitude: float

    # Devanagari, derived from the indices above rather than stored beside the
    # Latin names. Two parallel sets of names is two things to keep in step;
    # one set and a lookup is one.
    @property
    def tithi_hi(self) -> str:
        return K.TITHI_NAMES_HI[self.tithi_index % 15]

    @property
    def paksha_hi(self) -> str:
        return K.PAKSHA_HI[self.paksha]

    @property
    def nakshatra_hi(self) -> str:
        return K.NAKSHATRAS_HI[self.nakshatra_index]

    @property
    def yoga_hi(self) -> str:
        return K.YOGA_NAMES_HI[self.yoga_index]

    @property
    def karana_hi(self) -> str:
        return K.KARANA_HI[self.karana]

    @property
    def vara_hi(self) -> str:
        return K.VARA_NAMES_HI[self.vara_index]

    @property
    def vara_lord_hi(self) -> str:
        return K.GRAHA_HI[self.vara_lord]

    @property
    def masa_hi(self) -> str:
        return K.MASA_NAMES_HI[self.masa_index]


def _local_day_bounds(chart: Chart) -> tuple[float, float]:
    """Julian days of the local midnight before `chart` and the one after.

    Rise and set times belong to a civil day at a place, not to a 24-hour window
    hung off the moment — asking for "today's sunrise" at 9 pm must not answer
    with tomorrow's.
    """
    zone = ZoneInfo(chart.timezone)
    midnight = dt.datetime.combine(chart.birth_local.date(), dt.time(0, 0))
    start = midnight.replace(tzinfo=zone).astimezone(dt.timezone.utc)
    end = (midnight + dt.timedelta(days=1)).replace(tzinfo=zone).astimezone(dt.timezone.utc)
    return E.julian_day(start), E.julian_day(end)


def _masa_and_samvat(chart: Chart) -> tuple[int, int]:
    """The lunar month index (0 = Chaitra) and the Vikram Samvat year.

    Both fall out of one fact: a lunar month is named for the rashi the Sun
    enters during it, and the year turns with the month in which the Sun enters
    Mesha. So the month is read from where the Sun stood at the new moon that
    began it, and the year from whether that Chaitra has already started.
    """
    month_start = E.previous_new_moon(chart.julian_day)
    sun_at_start = E.all_positions(month_start)["Sun"].longitude
    sun_rashi = int(sun_at_start // K.RASHI_ARC)

    # The Sun advances one rashi per lunar month, so the sign it stands in at
    # the new moon is the one *before* the sign it will enter during the month.
    masa_index = (sun_rashi + 1) % 12

    # Which Vikram Samvat: the one that began at this Gregorian year's Chaitra,
    # unless that Chaitra is still ahead of us — in January the year that is
    # running began last March.
    year = chart.birth_local.year
    started = chart.julian_day >= E.chaitra_start(year)
    vikram = year + K.VIKRAM_OFFSET - (0 if started else 1)

    return masa_index, vikram


def panchang_for(chart: Chart) -> Panchang:
    """Compute the panchang at a chart's moment and place."""
    sun = chart.grahas["Sun"].placement.longitude
    moon = chart.grahas["Moon"].placement.longitude

    elongation = (moon - sun) % 360.0

    tithi_index = int(elongation // TITHI_ARC)
    tithi_percent = (elongation % TITHI_ARC) / TITHI_ARC * 100.0
    paksha = "Shukla" if tithi_index < 15 else "Krishna"

    karana_index = int(elongation // KARANA_ARC)
    yoga_index = int(((sun + moon) % 360.0) // YOGA_ARC)

    # The Vedic day runs sunrise to sunrise, so the vara belongs to the sunrise
    # that precedes the moment — not to the civil midnight date. Above the
    # polar circles there may be no sunrise, and we fall back to the civil day.
    rise_jd = E.sunrise(chart.julian_day, chart.latitude, chart.longitude)
    reference_jd = rise_jd if rise_jd is not None else chart.julian_day
    weekday = int(reference_jd + 1.5) % 7

    moon_placement = decompose(moon)

    masa_index, vikram = _masa_and_samvat(chart)
    day_start, day_end = _local_day_bounds(chart)
    sunrise_jd, sunset_jd = E.rise_set(
        "Sun", day_start, day_end, chart.latitude, chart.longitude
    )
    moonrise_jd, moonset_jd = E.rise_set(
        "Moon", day_start, day_end, chart.latitude, chart.longitude
    )

    return Panchang(
        tithi_index=tithi_index,
        tithi=K.TITHI_NAMES[tithi_index % 15],
        tithi_number=(tithi_index % 15) + 1,
        paksha=paksha,
        tithi_percent=tithi_percent,
        nakshatra_index=moon_placement.nakshatra_index,
        nakshatra=moon_placement.nakshatra,
        nakshatra_pada=moon_placement.pada,
        yoga_index=yoga_index,
        yoga=K.YOGA_NAMES[yoga_index],
        karana_index=karana_index,
        karana=_karana_name(karana_index),
        vara_index=weekday,
        vara=K.VARA_NAMES[weekday],
        vara_lord=K.VARA_LORDS[weekday],
        masa_index=masa_index,
        masa=K.MASA_NAMES[masa_index],
        vikram_samvat=vikram,
        shaka_samvat=vikram - K.SHAKA_BEHIND_VIKRAM,
        sunrise_jd=sunrise_jd,
        sunset_jd=sunset_jd,
        moonrise_jd=moonrise_jd,
        moonset_jd=moonset_jd,
        sun_longitude=sun,
        moon_longitude=moon,
    )

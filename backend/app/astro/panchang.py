"""Panchang: the five limbs of the Vedic calendar for a given moment.

Tithi, karana and yoga are all simple functions of the Sun-Moon relationship.
Tithi and karana use the *difference* of the two longitudes, so the ayanamsa
cancels and they are identical in tropical or sidereal terms. Yoga uses the
*sum*, where it does not cancel — so yoga must be computed sidereally, as it is
here.
"""

from __future__ import annotations

from dataclasses import dataclass

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

    nakshatra: str            # the Moon's, i.e. janma nakshatra
    nakshatra_pada: int

    yoga_index: int
    yoga: str

    karana_index: int
    karana: str

    vara: str
    vara_lord: str

    sun_longitude: float
    moon_longitude: float


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

    return Panchang(
        tithi_index=tithi_index,
        tithi=K.TITHI_NAMES[tithi_index % 15],
        tithi_number=(tithi_index % 15) + 1,
        paksha=paksha,
        tithi_percent=tithi_percent,
        nakshatra=moon_placement.nakshatra,
        nakshatra_pada=moon_placement.pada,
        yoga_index=yoga_index,
        yoga=K.YOGA_NAMES[yoga_index],
        karana_index=karana_index,
        karana=_karana_name(karana_index),
        vara=K.VARA_NAMES[weekday],
        vara_lord=K.VARA_LORDS[weekday],
        sun_longitude=sun,
        moon_longitude=moon,
    )

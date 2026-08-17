"""Vimshottari dasha: the 120-year planetary period cycle.

The whole system is fixed by one number — the Moon's position at birth. The
fraction of the janma nakshatra the Moon had already traversed is the fraction
of the first mahadasha already elapsed; everything after that is division.

Periods nest self-similarly: each level runs the same nine lords in the same
order, starting from its own lord, each taking the same proportion of the
parent period that it takes of the 120-year whole.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from . import constants as K
from .chart import Chart


@dataclass(frozen=True, slots=True)
class DashaPeriod:
    """One period at any nesting level."""

    lord: str
    lord_hi: str
    start: dt.datetime
    end: dt.datetime
    level: int                                  # 1 = maha, 2 = antar, 3 = pratyantar
    children: tuple["DashaPeriod", ...] = field(default=())

    @property
    def duration_days(self) -> float:
        return (self.end - self.start).total_seconds() / 86400.0

    @property
    def duration_years(self) -> float:
        return self.duration_days / K.DAYS_PER_YEAR

    def contains(self, moment: dt.datetime) -> bool:
        return self.start <= moment < self.end


def _years_to_delta(years: float) -> dt.timedelta:
    return dt.timedelta(days=years * K.DAYS_PER_YEAR)


def _lords_from(lord: str) -> list[str]:
    """The nine lords in Vimshottari order, rotated to begin at `lord`."""
    start = K.VIMSHOTTARI_ORDER.index(lord)
    return [K.VIMSHOTTARI_ORDER[(start + i) % 9] for i in range(9)]


def _subdivide(
    lord: str,
    start: dt.datetime,
    total_days: float,
    level: int,
    max_level: int,
) -> tuple[DashaPeriod, ...]:
    """Split a period into its sub-periods, recursively down to `max_level`."""
    if level > max_level:
        return ()

    periods: list[DashaPeriod] = []
    cursor = start

    for sub_lord in _lords_from(lord):
        share = K.VIMSHOTTARI_YEARS[sub_lord] / K.VIMSHOTTARI_TOTAL_YEARS
        sub_days = total_days * share
        sub_end = cursor + dt.timedelta(days=sub_days)

        periods.append(
            DashaPeriod(
                lord=sub_lord,
                lord_hi=K.GRAHA_HI[sub_lord],
                start=cursor,
                end=sub_end,
                level=level,
                children=_subdivide(sub_lord, cursor, sub_days, level + 1, max_level),
            )
        )
        cursor = sub_end

    return tuple(periods)


@dataclass(frozen=True, slots=True)
class VimshottariTimeline:
    """The full dasha sequence for one nativity."""

    janma_nakshatra: str
    janma_nakshatra_lord: str
    nakshatra_fraction_elapsed: float   # 0-1, portion traversed at birth
    balance_years: float                # remaining in the first mahadasha
    periods: tuple[DashaPeriod, ...]

    def at(self, moment: dt.datetime) -> list[DashaPeriod]:
        """The nested periods active at `moment`, outermost first.

        Returns an empty list outside the 120-year span the timeline covers.
        """
        active: list[DashaPeriod] = []
        candidates = self.periods

        while candidates:
            for period in candidates:
                if period.contains(moment):
                    active.append(period)
                    candidates = period.children
                    break
            else:
                break

        return active


def vimshottari(
    chart: Chart,
    levels: int = 3,
    cycles: int = 1,
) -> VimshottariTimeline:
    """Build the Vimshottari timeline for a chart.

    `levels` sets nesting depth (1 maha, 2 +antar, 3 +pratyantar). `cycles`
    extends past the first 120 years, which matters only because the first
    mahadasha starts partly consumed — one cycle still covers a full lifetime.
    """
    if not 1 <= levels <= 3:
        raise ValueError("levels must be 1, 2 or 3")

    moon = chart.grahas["Moon"].placement
    lord = moon.nakshatra_lord

    # Fraction of the janma nakshatra already traversed at birth.
    traversed = moon.longitude - (moon.nakshatra_index * K.NAKSHATRA_ARC)
    fraction = traversed / K.NAKSHATRA_ARC

    first_total_years = K.VIMSHOTTARI_YEARS[lord]
    balance_years = first_total_years * (1.0 - fraction)

    # The first mahadasha notionally began before birth; anchoring there keeps
    # every later boundary exact instead of accumulating rounding.
    birth = chart.birth_utc
    cycle_start = birth - _years_to_delta(first_total_years * fraction)

    periods: list[DashaPeriod] = []
    cursor = cycle_start

    for cycle in range(cycles):
        for maha_lord in _lords_from(lord):
            total_years = K.VIMSHOTTARI_YEARS[maha_lord]
            total_days = total_years * K.DAYS_PER_YEAR
            end = cursor + dt.timedelta(days=total_days)

            periods.append(
                DashaPeriod(
                    lord=maha_lord,
                    lord_hi=K.GRAHA_HI[maha_lord],
                    start=cursor,
                    end=end,
                    level=1,
                    children=_subdivide(maha_lord, cursor, total_days, 2, levels),
                )
            )
            cursor = end

    return VimshottariTimeline(
        janma_nakshatra=moon.nakshatra,
        janma_nakshatra_lord=lord,
        nakshatra_fraction_elapsed=fraction,
        balance_years=balance_years,
        periods=tuple(periods),
    )

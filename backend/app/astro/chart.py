"""Natal chart construction: turning raw longitudes into Vedic chart structure.

Every value here is derived arithmetically from an ephemeris longitude. There
is no interpretation, no judgement, and nothing probabilistic — given the same
birth data this module returns byte-identical output forever. Interpretation is
a separate layer's job.
"""

from __future__ import annotations

import datetime as dt
from dataclasses import dataclass, field

from . import constants as K
from . import ephemeris as E


# --- Longitude decomposition ------------------------------------------------


@dataclass(frozen=True, slots=True)
class Placement:
    """Where a single point falls, in every subdivision we care about."""

    longitude: float          # sidereal, 0-360
    rashi_index: int          # 0 = Mesha
    rashi: str
    rashi_en: str
    rashi_lord: str
    degree_in_rashi: float
    nakshatra_index: int      # 0 = Ashwini
    nakshatra: str
    nakshatra_lord: str
    pada: int                 # 1-4
    navamsa_index: int        # 0 = Mesha
    navamsa: str

    # Devanagari, derived rather than stored. Every one of these comes off an
    # index this dataclass already holds, so a Hindi name cannot drift out of
    # step with the Latin one it translates — which a second set of stored
    # fields would eventually do.
    @property
    def rashi_hi(self) -> str:
        return K.RASHIS_HI[self.rashi_index]

    @property
    def nakshatra_hi(self) -> str:
        return K.NAKSHATRAS_HI[self.nakshatra_index]

    @property
    def navamsa_hi(self) -> str:
        return K.RASHIS_HI[self.navamsa_index]

    @property
    def rashi_lord_hi(self) -> str:
        return K.GRAHA_HI[self.rashi_lord]

    @property
    def nakshatra_lord_hi(self) -> str:
        return K.GRAHA_HI[self.nakshatra_lord]

    @property
    def dms(self) -> str:
        """Degree within the rashi as a `12°34'56\"` string."""
        total = self.degree_in_rashi
        degrees = int(total)
        minutes_full = (total - degrees) * 60.0
        minutes = int(minutes_full)
        seconds = int(round((minutes_full - minutes) * 60.0))
        if seconds == 60:
            seconds = 0
            minutes += 1
        if minutes == 60:
            minutes = 0
            degrees += 1
        return f"{degrees}°{minutes:02d}'{seconds:02d}\""


# Rashi (12), nakshatra (27) and pada/navamsa (108) subdivisions all refine into
# the same 3°20' arc, so snapping longitudes to that grid keeps every
# subdivision mutually consistent.
_FINEST_DIVISIONS = 108
_SNAP_EPSILON = 1e-9


def _arc_index(longitude: float, divisions: int) -> int:
    """Index of a longitude among `divisions` equal zodiac arcs.

    Scales before dividing — `lon * n / 360` rather than `lon // (360 / n)` —
    because arcs like 13°20' are not representable in binary floating point and
    dividing by the stored approximation puts exactly-on-boundary longitudes one
    arc too low. Values landing within `_SNAP_EPSILON` of an arc boundary snap
    to it, so 40°, which is precisely three nakshatras, reads as the start of
    the fourth rather than the tail of the third. The window is ~1.2e-5
    arcseconds wide — orders of magnitude below any achievable precision, but
    enough to stop a silent off-by-one into the wrong Vimshottari lord.
    """
    scaled = (longitude % 360.0) * divisions / 360.0
    nearest = round(scaled)
    index = int(nearest) if abs(scaled - nearest) < _SNAP_EPSILON else int(scaled)
    return index % divisions


def _snap_to_fine_grid(longitude: float) -> tuple[float, int]:
    """Normalize a longitude onto the 3°20' grid, returning it and its arc index.

    Both are returned together because they must agree: snapping the index
    without snapping the longitude lets 359.9999999999° report as Mesha 359°,
    the sign taken from the wrapped index and the degree from the unwrapped
    value.
    """
    lon = longitude % 360.0
    scaled = lon * _FINEST_DIVISIONS / 360.0
    nearest = round(scaled)

    if abs(scaled - nearest) < _SNAP_EPSILON:
        fine_index = int(nearest) % _FINEST_DIVISIONS
        return fine_index * (360.0 / _FINEST_DIVISIONS), fine_index

    return lon, int(scaled) % _FINEST_DIVISIONS


def decompose(longitude: float) -> Placement:
    """Break a sidereal longitude into rashi, nakshatra, pada and navamsa."""
    # Rashis, nakshatras and padas all refine into the same 3°20' grid, so one
    # snapped index drives every subdivision. Deriving the rest by integer
    # arithmetic makes disagreement between them structurally impossible —
    # recomputing each from the float longitude reintroduces the rounding this
    # is here to defeat.
    lon, fine_index = _snap_to_fine_grid(longitude)

    rashi_index = fine_index // 9        # 9 navamsa arcs per rashi
    nakshatra_index = fine_index // 4    # 4 padas per nakshatra
    pada = (fine_index % 4) + 1

    # Navamsa by the continuous-arc rule: counting 3°20' arcs from 0° Mesha and
    # taking the result mod 12 reproduces the classical chara/sthira/dwiswabhava
    # starting-sign rules exactly, without special-casing modality.
    navamsa_index = fine_index % 12

    return Placement(
        longitude=lon,
        rashi_index=rashi_index,
        rashi=K.RASHIS[rashi_index],
        rashi_en=K.RASHIS_EN[rashi_index],
        rashi_lord=K.RASHI_LORDS[rashi_index],
        # Derived from the index, not a second `% 30`, so degree and sign can
        # never disagree about which side of a boundary the point is on. The
        # clamp catches a longitude a few ulps below a boundary that snapped up.
        degree_in_rashi=max(0.0, lon - rashi_index * K.RASHI_ARC),
        nakshatra_index=nakshatra_index,
        nakshatra=K.NAKSHATRAS[nakshatra_index],
        nakshatra_lord=K.NAKSHATRA_LORDS[nakshatra_index],
        pada=pada,
        navamsa_index=navamsa_index,
        navamsa=K.RASHIS[navamsa_index],
    )


def divisional_sign(longitude: float, division: int) -> int:
    """Sign index in the D-`division` varga chart, by the continuous-arc rule.

    Correct for the vargas that follow uniform equal division counted from
    Mesha (D1, D3, D9, D12...). Vargas with irregular schemes (D4, D7, D10,
    D16...) follow per-sign starting rules that this does not encode, so it is
    used only for D9 today.
    """
    if division < 1:
        raise ValueError("division must be >= 1")
    return _arc_index(longitude, 12 * division) % 12


# --- Chart bodies -----------------------------------------------------------


@dataclass(frozen=True, slots=True)
class GrahaPosition:
    """One graha placed in the chart."""

    graha: str
    graha_hi: str
    placement: Placement
    house: int                # 1-12, whole-sign from lagna
    speed: float
    retrograde: bool
    combust: bool = False


@dataclass(frozen=True, slots=True)
class Chart:
    """A complete deterministic natal chart."""

    # Inputs, echoed back so a chart is self-describing.
    birth_local: dt.datetime
    birth_utc: dt.datetime
    timezone: str
    latitude: float
    longitude: float

    # Computation provenance.
    julian_day: float
    ayanamsa: float
    ayanamsa_name: str
    ephemeris_mode: str

    lagna: Placement
    grahas: dict[str, GrahaPosition]
    houses: dict[int, str] = field(default_factory=dict)      # house -> rashi
    house_lords: dict[int, str] = field(default_factory=dict)  # house -> lord

    def graha_in_house(self, house: int) -> list[str]:
        """Names of grahas occupying a house."""
        return [g.graha for g in self.grahas.values() if g.house == house]

    @property
    def moon_rashi(self) -> str:
        """Rashi of the Moon — the `rashi` an Indian user means colloquially."""
        return self.grahas["Moon"].placement.rashi

    @property
    def janma_nakshatra(self) -> str:
        return self.grahas["Moon"].placement.nakshatra

    @property
    def moon_rashi_hi(self) -> str:
        return self.grahas["Moon"].placement.rashi_hi

    @property
    def janma_nakshatra_hi(self) -> str:
        return self.grahas["Moon"].placement.nakshatra_hi

    @property
    def ayanamsa_name_hi(self) -> str:
        """Falls back to the English label rather than to nothing: an unnamed
        correction is worse than one named in the other language."""
        return K.AYANAMSA_NAMES_HI.get(self.ayanamsa_name, self.ayanamsa_name)


# Maximum elongation from the Sun, in degrees, within which a graha is
# traditionally considered combust (asta). Values follow the Surya Siddhanta
# convention used by most modern panchangs.
_COMBUSTION_ORB: dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus": 10.0,
    "Saturn": 15.0,
}


def _angular_separation(a: float, b: float) -> float:
    """Smallest angle between two longitudes, 0-180."""
    diff = abs(a - b) % 360.0
    return diff if diff <= 180.0 else 360.0 - diff


def build_chart(
    birth_local: dt.datetime,
    latitude: float,
    longitude: float,
    tz_name: str | None = None,
) -> Chart:
    """Compute a full natal chart from birth date, time and coordinates.

    `birth_local` must be naive local clock time at the birth place — the time
    written on the birth certificate.
    """
    if not -90.0 <= latitude <= 90.0:
        raise ValueError(f"latitude out of range: {latitude}")
    if not -180.0 <= longitude <= 180.0:
        raise ValueError(f"longitude out of range: {longitude}")

    birth_utc, resolved_tz = E.to_utc(birth_local, latitude, longitude, tz_name)
    jd = E.julian_day(birth_utc)

    lagna = decompose(E.ascendant(jd, latitude, longitude))
    raw = E.all_positions(jd)
    sun_longitude = raw["Sun"].longitude

    grahas: dict[str, GrahaPosition] = {}
    for name in K.GRAHAS:
        pos = raw[name]
        placement = decompose(pos.longitude)
        house = ((placement.rashi_index - lagna.rashi_index) % 12) + 1

        orb = _COMBUSTION_ORB.get(name)
        combust = (
            orb is not None
            and _angular_separation(pos.longitude, sun_longitude) <= orb
        )

        grahas[name] = GrahaPosition(
            graha=name,
            graha_hi=K.GRAHA_HI[name],
            placement=placement,
            house=house,
            speed=pos.speed,
            # Rahu and Ketu are perpetually retrograde by definition rather than
            # by measured speed.
            retrograde=True if name in K.SHADOW_GRAHAS else pos.speed < 0,
            combust=combust,
        )

    houses = {
        h: K.RASHIS[(lagna.rashi_index + h - 1) % 12]
        for h in range(1, 13)
    }
    house_lords = {
        h: K.RASHI_LORDS[(lagna.rashi_index + h - 1) % 12]
        for h in range(1, 13)
    }

    return Chart(
        birth_local=birth_local,
        birth_utc=birth_utc,
        timezone=resolved_tz,
        latitude=latitude,
        longitude=longitude,
        julian_day=jd,
        ayanamsa=E.ayanamsa(jd),
        ayanamsa_name="Lahiri (Chitrapaksha)",
        ephemeris_mode=E.EPHEMERIS_MODE,
        lagna=lagna,
        grahas=grahas,
        houses=houses,
        house_lords=house_lords,
    )


def navamsa_chart(chart: Chart) -> dict[str, str]:
    """D9 (navamsa) sign for the lagna and each graha."""
    result = {"Ascendant": K.RASHIS[chart.lagna.navamsa_index]}
    for name, graha in chart.grahas.items():
        result[name] = K.RASHIS[graha.placement.navamsa_index]
    return result

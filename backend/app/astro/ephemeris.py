"""Thin, deterministic wrapper around the Skyfield / JPL ephemeris.

This module is the *only* place that talks to an astronomy library. Everything
above it works with plain Python values, which is what made swapping the
underlying ephemeris a single-file change.

Why Skyfield and not the Swiss Ephemeris:

- **Licence.** Swiss Ephemeris is AGPL-3.0 or a paid commercial licence; the
  AGPL network clause would oblige us to hand the full service source to every
  user. Skyfield is MIT and JPL's ephemerides are public domain.
- **Portability.** `pyswisseph` is a C extension whose newest wheels stop at
  CPython 3.11, so anything newer needed a compiler. Skyfield is pure Python.
- **No global state.** `pyswisseph` kept its configuration in thread-local
  storage, so a worker thread silently computed with the wrong ayanamsa. There
  is no equivalent hazard here — nothing below is configured process-wide.
- **Accuracy.** JPL DE440 is the source data rather than an analytic fit.

Agreement with the previous Swiss Ephemeris implementation, measured across
charts from 1902 to 2049 in both hemispheres: planets within 1.7", the
ascendant within 0.001", and the lunar node within 19" (see `_mean_node`).
"""

from __future__ import annotations

import datetime as dt
import functools
import math
import os
import threading
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from skyfield.api import Loader, wgs84
from skyfield.nutationlib import iau2000b, mean_obliquity
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo

from . import constants as K

# --- Ephemeris configuration ------------------------------------------------

# DE440s covers 1849-12-25 to 2150-01-21 in 32 MB, which spans every plausible
# birth date with room to spare. DE421 is half the size but stops at 2053.
_DEFAULT_DIR = Path(__file__).resolve().parents[2] / "data"

EPHEMERIS_DIR = Path(os.environ.get("EPHEMERIS_DIR", _DEFAULT_DIR))
EPHEMERIS_FILE = os.environ.get("EPHEMERIS_FILE", "de440s.bsp")
EPHEMERIS_MODE = Path(EPHEMERIS_FILE).stem

# Skyfield's barycentre segments are what DE440s actually carries for the
# planets; for Mercury and Venus the barycentre and the body coincide to far
# below our resolution.
_BODIES: dict[str, str] = {
    "Sun": "sun",
    "Moon": "moon",
    "Mercury": "mercury barycenter",
    "Venus": "venus barycenter",
    "Mars": "mars barycenter",
    "Jupiter": "jupiter barycenter",
    "Saturn": "saturn barycenter",
}

# Half-window for the central difference used to get longitude speed.
_SPEED_DELTA_DAYS = 0.5 / 24.0

_kernel_lock = threading.Lock()
_kernel: tuple | None = None


def _load_kernel():
    """Load the timescale and ephemeris once, on first use.

    Deliberately lazy: importing this module must stay cheap and offline, and
    the kernel is a 32 MB download the first time it is needed. Deployments
    should pre-fetch it during the build rather than on the first request.
    """
    global _kernel
    if _kernel is not None:
        return _kernel

    with _kernel_lock:
        if _kernel is None:
            EPHEMERIS_DIR.mkdir(parents=True, exist_ok=True)
            loader = Loader(str(EPHEMERIS_DIR), verbose=False)
            timescale = loader.timescale()
            ephemeris = loader(EPHEMERIS_FILE)
            _kernel = (timescale, ephemeris, ephemeris["earth"])

    return _kernel


# --- Ayanamsa ---------------------------------------------------------------

# Lahiri (Chitrapaksha) mean ayanamsa, in degrees, as a quadratic in Julian
# centuries of UT from J2000. Fitted to the Swiss Ephemeris implementation,
# which it reproduces to 0.0001" over 1900-2100 and 0.0006" over 1700-2300 —
# the underlying model really is a quadratic, so this is a restatement rather
# than an approximation.
_LAHIRI = (23.857092389003597, 1.3968879758932495, 3.070584760188855e-4)


def _mean_ayanamsa(jd: float | np.ndarray) -> float | np.ndarray:
    T = (jd - 2451545.0) / 36525.0
    c0, c1, c2 = _LAHIRI
    return c0 + c1 * T + c2 * T * T


def _nutation_longitude(t) -> float | np.ndarray:
    """Nutation in longitude (Δψ) in degrees, IAU 2000B."""
    dpsi, _deps = iau2000b(t.tt)
    return dpsi * 1e-7 / 3600.0


def _effective_ayanamsa(jd, t):
    """The offset to subtract from apparent longitudes to get sidereal ones.

    Apparent positions are referred to the *true* equinox of date while the
    ayanamsa is measured from the *mean* equinox, so the nutation in longitude
    has to be folded in. Missing this shifts every graha by up to 17" — a
    uniform error that is easy to mistake for a correct chart.
    """
    return _mean_ayanamsa(jd) + _nutation_longitude(t)


def ayanamsa(jd: float) -> float:
    """Lahiri mean ayanamsa in degrees, for reporting.

    This is the value panchangs quote, and matches Swiss Ephemeris'
    `get_ayanamsa_ut`. The conversion of positions uses
    `_effective_ayanamsa`, which additionally accounts for nutation.
    """
    return float(_mean_ayanamsa(jd))


# --- Time handling ----------------------------------------------------------

_tz_finder = TimezoneFinder()


@functools.lru_cache(maxsize=4096)
def timezone_for(latitude: float, longitude: float) -> str:
    """Resolve an IANA timezone name from coordinates.

    Falls back to UTC only over open ocean, where `timezonefinder` has no
    polygon. Any real birth place resolves.
    """
    name = _tz_finder.timezone_at(lat=latitude, lng=longitude)
    return name or "UTC"


def to_utc(
    local_naive: dt.datetime,
    latitude: float,
    longitude: float,
    tz_name: str | None = None,
) -> tuple[dt.datetime, str]:
    """Convert a naive local birth datetime to UTC.

    Returns the UTC datetime and the timezone name actually used. Historical
    offsets matter here: India ran on +05:30 from 1955 but had +06:30 during
    parts of WWII, and `zoneinfo` carries the full tzdata history, so a 1942
    Kolkata birth resolves correctly.

    Ambiguous local times (the repeated hour when DST ends) resolve to the
    first, pre-transition occurrence; nonexistent times (the skipped hour when
    DST starts) are shifted forward by the gap. Both are deterministic.
    """
    if local_naive.tzinfo is not None:
        raise ValueError("birth datetime must be naive local time, not tz-aware")

    name = tz_name or timezone_for(latitude, longitude)
    zone = ZoneInfo(name)
    localized = local_naive.replace(tzinfo=zone, fold=0)
    return localized.astimezone(dt.timezone.utc), name


def julian_day(utc: dt.datetime) -> float:
    """Julian day for a timezone-aware UTC datetime, Gregorian calendar.

    Computed arithmetically rather than through Skyfield so that UT is taken
    as UTC exactly, matching how the rest of the engine treats birth times.
    """
    if utc.tzinfo is None:
        raise ValueError("expected a timezone-aware UTC datetime")
    utc = utc.astimezone(dt.timezone.utc)

    a = (14 - utc.month) // 12
    y = utc.year + 4800 - a
    m = utc.month + 12 * a - 3
    jdn = (
        utc.day
        + (153 * m + 2) // 5
        + 365 * y
        + y // 4
        - y // 100
        + y // 400
        - 32045
    )
    fraction = (
        (utc.hour - 12) / 24.0
        + utc.minute / 1440.0
        + (utc.second + utc.microsecond / 1e6) / 86400.0
    )
    return jdn + fraction


def from_julian_day(jd: float) -> dt.datetime:
    """Inverse of :func:`julian_day` — Julian day back to an aware UTC datetime."""
    jdn = math.floor(jd + 0.5)
    fraction = jd + 0.5 - jdn

    a = jdn + 32044
    b = (4 * a + 3) // 146097
    c = a - 146097 * b // 4
    d = (4 * c + 3) // 1461
    e = c - 1461 * d // 4
    m = (5 * e + 2) // 153

    day = e - (153 * m + 2) // 5 + 1
    month = m + 3 - 12 * (m // 10)
    year = 100 * b + d - 4800 + m // 10

    base = dt.datetime(year, month, day, tzinfo=dt.timezone.utc)
    return base + dt.timedelta(seconds=round(fraction * 86400.0, 3))


# --- Positions --------------------------------------------------------------


@dataclass(frozen=True, slots=True)
class RawPosition:
    """A body's sidereal position at one instant."""

    longitude: float       # sidereal ecliptic longitude, 0-360
    latitude: float        # ecliptic latitude
    distance: float        # AU
    speed: float           # longitude degrees/day; negative means retrograde


def _wrap180(degrees):
    return (degrees + 180.0) % 360.0 - 180.0


def _mean_node(t) -> np.ndarray:
    """Mean lunar node (Rahu) in degrees, tropical, Meeus' polynomial.

    Swiss Ephemeris' mean node carries small periodic terms this omits, so the
    two disagree by up to ~19". A nakshatra pada is 12000" wide, so this only
    changes a reading if Rahu sits within 19" of a pada boundary — and there
    the "right" answer depends on which mean-node definition you accept
    anyway, with published panchangs differing by more than this.
    """
    T = (t.tt - 2451545.0) / 36525.0
    return (
        125.0445479
        - 1934.1362891 * T
        + 0.0020754 * T**2
        + T**3 / 467441.0
        - T**4 / 60616000.0
    ) % 360.0


def all_positions(jd: float) -> dict[str, RawPosition]:
    """Sidereal positions of all nine grahas, in traditional order.

    Every body is evaluated at three epochs at once — the moment plus and minus
    half an hour — so the central difference that yields longitude speed costs
    almost nothing on top of the position itself.
    """
    timescale, ephemeris, earth = _load_kernel()

    jds = np.array(
        [jd - _SPEED_DELTA_DAYS, jd, jd + _SPEED_DELTA_DAYS], dtype=float
    )
    try:
        t = timescale.ut1_jd(jds)
        offset = _effective_ayanamsa(jds, t)

        results: dict[str, RawPosition] = {}
        for name, key in _BODIES.items():
            latitudes, longitudes, distances = (
                earth.at(t).observe(ephemeris[key]).apparent().ecliptic_latlon(epoch=t)
            )
            sidereal = (longitudes.degrees - offset) % 360.0
            speed = _wrap180(sidereal[2] - sidereal[0]) / (2 * _SPEED_DELTA_DAYS)

            results[name] = RawPosition(
                longitude=float(sidereal[1]),
                latitude=float(latitudes.degrees[1]),
                distance=float(distances.au[1]),
                speed=float(speed),
            )

        nodes = (_mean_node(t) - offset) % 360.0
    except (ValueError, IndexError) as exc:
        raise ValueError(
            f"birth date is outside the {EPHEMERIS_MODE} ephemeris range"
        ) from exc

    node_speed = _wrap180(nodes[2] - nodes[0]) / (2 * _SPEED_DELTA_DAYS)
    results["Rahu"] = RawPosition(
        longitude=float(nodes[1]), latitude=0.0, distance=0.0, speed=float(node_speed)
    )
    # Ketu is not a body — it is Rahu's exact opposite point, always.
    results["Ketu"] = RawPosition(
        longitude=float((nodes[1] + 180.0) % 360.0),
        latitude=0.0,
        distance=0.0,
        speed=float(node_speed),
    )

    return {name: results[name] for name in K.GRAHAS}


def position(jd: float, graha: str) -> RawPosition:
    """Sidereal position of one graha."""
    if graha not in K.GRAHAS:
        raise KeyError(f"unknown graha: {graha!r}")
    return all_positions(jd)[graha]


def ascendant(jd: float, latitude: float, longitude: float) -> float:
    """Sidereal ascendant (lagna) in degrees.

    The ascendant is where the ecliptic meets the eastern horizon, which
    depends only on local sidereal time, the obliquity and the observer's
    latitude — no house system enters into it. Houses elsewhere in the engine
    are whole-sign, the standard North and South Indian convention.

    Reproduces Swiss Ephemeris to within 0.001".
    """
    timescale, _ephemeris, _earth = _load_kernel()
    t = timescale.ut1_jd(jd)

    _dpsi, deps = iau2000b(t.tt)
    obliquity = (mean_obliquity(t.tdb) + deps * 1e-7) / 3600.0

    # Right ascension of the midheaven, i.e. local apparent sidereal time.
    ramc = (t.gast * 15.0 + longitude) % 360.0

    e = math.radians(obliquity)
    r = math.radians(ramc)
    phi = math.radians(latitude)

    tropical = math.degrees(
        math.atan2(
            math.cos(r),
            -(math.sin(r) * math.cos(e) + math.tan(phi) * math.sin(e)),
        )
    )
    return float((tropical - _effective_ayanamsa(jd, t)) % 360.0)


def sunrise(jd: float, latitude: float, longitude: float) -> float | None:
    """Julian day of the sunrise preceding or at `jd`, or None in polar day/night.

    Needed for vara (weekday), which in the Vedic system changes at sunrise
    rather than at midnight.
    """
    from skyfield import almanac

    timescale, ephemeris, _earth = _load_kernel()
    location = wgs84.latlon(latitude, longitude)

    # A 36-hour lookback is enough to contain a sunrise at any latitude where
    # the sun rises at all.
    try:
        start = timescale.ut1_jd(jd - 1.5)
        end = timescale.ut1_jd(jd)
        times, events = almanac.find_discrete(
            start, end, almanac.sunrise_sunset(ephemeris, location)
        )
    except (ValueError, IndexError):
        return None

    risings = [
        time.ut1 for time, event in zip(times, events) if event == 1 and time.ut1 <= jd
    ]
    return max(risings) if risings else None

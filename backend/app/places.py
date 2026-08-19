"""Built-in place lookup for birth coordinates.

Deliberately a bundled dataset rather than a geocoding API call: birth place
search happens on the onboarding screen, where a network round trip per
keystroke is the difference between the app feeling instant and feeling like
every other astrology app. Swapping in a real geocoder later means replacing
`search()` alone — nothing else imports the table.

Coverage is India-first — roughly three thousand places, every town above twenty
thousand people plus every administrative headquarters, which is tier-1 through
tier-3 — plus the world cities an Indian diaspora user is most likely to have
been born in. The table itself lives in `places_data.py`; the Indian half of it
is generated from GeoNames by `scripts/build_gazetteer.py`.
"""

from __future__ import annotations

import unicodedata
from functools import lru_cache

from .places_data import PLACES as _PLACES
from .schemas import PlaceOut


def _fold(text: str) -> str:
    """Casefold and strip accents so `Bengaluru` matches `bengaluru`."""
    decomposed = unicodedata.normalize("NFKD", text)
    stripped = "".join(c for c in decomposed if not unicodedata.combining(c))
    return stripped.casefold().strip()


@lru_cache(maxsize=1)
def _index() -> tuple[tuple[str, PlaceOut], ...]:
    """Pre-folded search keys paired with their place."""
    return tuple(
        (
            _fold(f"{name} {admin} {country}"),
            PlaceOut(
                name=name,
                admin=admin,
                country=country,
                latitude=lat,
                longitude=lon,
            ),
        )
        for name, admin, country, lat, lon in _PLACES
    )


def search(query: str, limit: int = 10) -> list[PlaceOut]:
    """Find places matching `query`, best matches first.

    Ranking is prefix-match on the city name, then any substring hit. Over three
    thousand entries that is still a sub-millisecond linear scan, and it keeps
    the behaviour obvious; a real geocoder would replace this wholesale.
    """
    needle = _fold(query)
    if not needle:
        return []

    prefix: list[PlaceOut] = []
    contains: list[PlaceOut] = []

    for key, place in _index():
        city = _fold(place.name)
        if city.startswith(needle):
            prefix.append(place)
        elif needle in key:
            contains.append(place)

        if len(prefix) >= limit:
            break

    return (prefix + contains)[:limit]

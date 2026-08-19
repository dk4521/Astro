"""Regenerate `app/places_data.py` from the GeoNames dump.

The birth-place picker needs a town in Bihar with forty thousand people just as
much as it needs Mumbai, and typing those coordinates by hand is how a chart
ends up cast for the wrong village. So the Indian half of the table is generated
from GeoNames rather than written: run this script, commit the diff, and the
provenance of every coordinate is a public dataset instead of somebody's memory.

    ./.venv/bin/python scripts/build_gazetteer.py

Curated entries — the ones in the file before this script existed — are kept
exactly as they are and placed first. They carry deliberate choices the dump
does not: modern spellings (Bengaluru, not Bangalore), both halves of a rename
(Allahabad and Prayagraj), pilgrimage towns people are born near, and the
non-Indian cities an Indian diaspora user is likely to need. Generated entries
are appended, ordered by population, and skipped when they duplicate a curated
one.

Data: GeoNames (https://download.geonames.org/export/dump/), CC BY 4.0.
"""

from __future__ import annotations

import io
import pathlib
import sys
import unicodedata
import urllib.request
import zipfile

DUMP = "https://download.geonames.org/export/dump/IN.zip"
ADMIN1 = "https://download.geonames.org/export/dump/admin1CodesASCII.txt"

# Tier-3 in the Indian classification starts around twenty thousand people. Below
# that the dump is mostly villages, and the picker becomes harder to use rather
# than more complete.
MIN_POPULATION = 20_000

# Populated places only, and only the kinds that are somewhere a person lives.
# PPLX (neighbourhood) and PPLL (locality) are dropped: they duplicate the parent
# city at coordinates that make no difference to a chart. PPLQ/PPLW/PPLH are
# abandoned, destroyed or historical.
KEEP_CODES = {"PPL", "PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC", "PPLG"}

# Admin capitals are kept whatever the dump says their population is: a district
# headquarters is a place people are born in and register a birth in.
ALWAYS_KEEP = {"PPLA", "PPLA2", "PPLA3", "PPLA4", "PPLC"}

ALIAS_NOTE = """\
# Older and colloquial names, each carrying the coordinates of the city it names.
# A user born in 1972 types "Bombay", not "Mumbai", and the dump only knows the
# current spelling — so without these the picker returns nothing for exactly the
# people most likely to be looking. Ranked after the curated cities so searching
# the modern name still puts the modern name first.
"""

ROOT = pathlib.Path(__file__).resolve().parent.parent
TARGET = ROOT / "app" / "places_data.py"


def fold(text: str) -> str:
    decomposed = unicodedata.normalize("NFKD", text)
    return "".join(c for c in decomposed if not unicodedata.combining(c)).casefold().strip()


def fetch(url: str) -> bytes:
    print(f"  fetching {url}", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=180) as response:
        return response.read()


def admin1_names() -> dict[str, str]:
    """`IN.09` -> `Uttar Pradesh`."""
    names = {}
    for line in fetch(ADMIN1).decode("utf-8").splitlines():
        code, name, _ascii, _id = line.split("\t")
        if code.startswith("IN."):
            names[code.split(".", 1)[1]] = name
    return names


def geonames_rows(states: dict[str, str]) -> list[tuple[str, str, str, float, float, int]]:
    """One row per distinct city, highest-population duplicate winning."""
    archive = zipfile.ZipFile(io.BytesIO(fetch(DUMP)))
    best: dict[tuple[str, str], tuple[str, str, str, float, float, int]] = {}

    with archive.open("IN.txt") as handle:
        for raw in io.TextIOWrapper(handle, encoding="utf-8"):
            f = raw.rstrip("\n").split("\t")
            if len(f) < 15 or f[6] != "P" or f[7] not in KEEP_CODES:
                continue
            population = int(f[14] or 0)
            if population < MIN_POPULATION and f[7] not in ALWAYS_KEEP:
                continue
            state = states.get(f[10])
            if not state:
                continue
            name = (f[2] or f[1]).strip()
            if not name:
                continue
            key = (fold(name), state)
            row = (name, state, "India", float(f[4]), float(f[5]), population)
            if key not in best or population > best[key][5]:
                best[key] = row

    return sorted(best.values(), key=lambda r: (-r[5], r[0]))


def preserved() -> tuple[list[tuple], list[tuple], list[tuple]]:
    """The three hand-written blocks, read back from the file being rewritten.

    Deliberately not `places.PLACES`, which is all four blocks concatenated:
    reading that would fold the previous run's generated entries into the
    curated one and grow the file a little more on every run.
    """
    sys.path.insert(0, str(ROOT))
    from app import places_data

    return (
        list(places_data._CURATED_INDIA),
        list(places_data._ALIASES),
        list(places_data._WORLD),
    )


def render(rows: list[tuple], indent: str = "    ") -> str:
    return "".join(
        f'{indent}("{name}", "{admin}", "{country}", {lat:.4f}, {lon:.4f}),\n'
        for name, admin, country, lat, lon in rows
    )


def main() -> None:
    india_curated, aliases, world = preserved()
    # Aliases count as taken: the dump listing "Bardhaman" separately would put a
    # second entry at the same coordinates.
    seen = {(fold(n), a) for n, a, _c, _la, _lo in india_curated + aliases}

    states = admin1_names()
    added = [
        (name, state, country, lat, lon)
        for name, state, country, lat, lon, _pop in geonames_rows(states)
        if (fold(name), state) not in seen
    ]

    TARGET.write_text(
        '''"""The place table, kept out of `places.py` so the search logic stays readable.

Two blocks, in the order the picker should rank them. `_CURATED_INDIA` is
hand-written: modern spellings, both halves of a rename, and the pilgrimage
towns people are born near. `_GEONAMES_INDIA` is generated from the GeoNames
dump by `scripts/build_gazetteer.py` — every Indian place above twenty thousand
people, plus every administrative headquarters, which is tier-1 through tier-3
coverage. `_ALIASES` carries the older names — Bombay, Calcutta, Trivandrum —
that the dump no longer knows. `_WORLD` is hand-written for the diaspora.

Do not edit the generated block by hand; rerun the script. Corrections belong in
the curated block, which the script never touches and always ranks first.

Indian place data: GeoNames (https://download.geonames.org/export/dump/),
licensed CC BY 4.0.
"""

from __future__ import annotations

# name, admin (state / region), country, latitude, longitude
Place = tuple[str, str, str, float, float]

_CURATED_INDIA: tuple[Place, ...] = (
'''
        + render(india_curated)
        + ")\n\n"
        + ALIAS_NOTE
        + "_ALIASES: tuple[Place, ...] = (\n"
        + render(aliases)
        + ")\n\n_GEONAMES_INDIA: tuple[Place, ...] = (\n"
        + render(added)
        + ")\n\n_WORLD: tuple[Place, ...] = (\n"
        + render(world)
        + ")\n\nPLACES: tuple[Place, ...] = "
        + "_CURATED_INDIA + _ALIASES + _GEONAMES_INDIA + _WORLD\n"
    )

    total = len(india_curated) + len(aliases) + len(added) + len(world)
    print(
        f"{len(india_curated)} curated + {len(aliases)} aliases + {len(added)} "
        f"generated Indian places + {len(world)} elsewhere = {total}",
        file=sys.stderr,
    )


if __name__ == "__main__":
    main()

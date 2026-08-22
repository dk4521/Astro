"""Rendering a chart as facts the model reads.

The model never receives raw JSON. It receives a compact, labelled brief, for
three reasons: JSON costs roughly twice the tokens for the same content, its
nesting invites the model to reason about structure instead of meaning, and a
flat labelled block is far easier to check an answer against afterwards.

Nothing here interprets. Every line is a restatement of what the engine
computed.
"""

from __future__ import annotations

import datetime as dt

from ..astro import Chart, Panchang, VimshottariTimeline, navamsa_chart


def _degrees(value: float) -> str:
    return f"{value:.2f}"


def chart_facts(chart: Chart) -> str:
    """The natal chart as a labelled fact block."""
    lines = [
        "BIRTH",
        f"  local: {chart.birth_local:%Y-%m-%d %H:%M} ({chart.timezone})",
        f"  place: {chart.latitude:.4f}, {chart.longitude:.4f}",
        "",
        "ASCENDANT (lagna)",
        f"  {chart.lagna.rashi} ({chart.lagna.rashi_en}) {chart.lagna.dms}"
        f" — {chart.lagna.nakshatra} pada {chart.lagna.pada}"
        f", sign ruler {chart.lagna.rashi_lord}",
        "",
        "GRAHAS  (house numbers are whole-sign from the lagna)",
    ]

    for graha in chart.grahas.values():
        placement = graha.placement
        notes = []
        if graha.retrograde:
            notes.append("retrograde")
        if graha.combust:
            notes.append("combust")
        suffix = f"  [{', '.join(notes)}]" if notes else ""

        lines.append(
            f"  {graha.graha:<8} {placement.rashi} ({placement.rashi_en})"
            f" {placement.dms}, house {graha.house}"
            f" — {placement.nakshatra} pada {placement.pada}"
            f", nakshatra lord {placement.nakshatra_lord}{suffix}"
        )

    lines += ["", "HOUSES  (whole-sign; house -> rashi, ruler)"]
    for house in range(1, 13):
        occupants = chart.graha_in_house(house)
        occupied = f"  occupied by {', '.join(occupants)}" if occupants else ""
        lines.append(
            f"  {house:>2}. {chart.houses[house]}"
            f" (ruler {chart.house_lords[house]}){occupied}"
        )

    lines += ["", "NAVAMSA (D9)"]
    for body, sign in navamsa_chart(chart).items():
        lines.append(f"  {body:<10} {sign}")

    lines += [
        "",
        "COMPUTATION",
        f"  ayanamsa: {chart.ayanamsa_name} {_degrees(chart.ayanamsa)}°",
        "  house system: whole-sign",
        f"  ephemeris: JPL {chart.ephemeris_mode}",
    ]

    return "\n".join(lines)


def panchang_facts(panchang: Panchang) -> str:
    """Panchang at the birth moment."""
    return "\n".join(
        [
            "PANCHANG AT BIRTH",
            f"  tithi: {panchang.paksha} {panchang.tithi}"
            f" ({panchang.tithi_percent:.0f}% elapsed)",
            f"  nakshatra: {panchang.nakshatra} pada {panchang.nakshatra_pada}",
            f"  yoga: {panchang.yoga}",
            f"  karana: {panchang.karana}",
            f"  vara: {panchang.vara} (ruled by {panchang.vara_lord})",
        ]
    )


def dasha_facts(timeline: VimshottariTimeline, as_of: dt.datetime) -> str:
    """The Vimshottari periods running now, plus what comes next."""
    active = timeline.at(as_of)
    labels = ("Mahadasha", "Antardasha", "Pratyantardasha")

    lines = [
        "VIMSHOTTARI DASHA",
        f"  janma nakshatra: {timeline.janma_nakshatra}"
        f" (lord {timeline.janma_nakshatra_lord})",
        f"  balance at birth: {timeline.balance_years:.2f} years of"
        f" {timeline.janma_nakshatra_lord}",
        f"  as of: {as_of:%Y-%m-%d}",
    ]

    if not active:
        lines.append("  currently: outside the computed 120-year cycle")
        return "\n".join(lines)

    lines.append("  running now:")
    for label, period in zip(labels, active):
        lines.append(
            f"    {label}: {period.lord}"
            f"  {period.start:%Y-%m-%d} to {period.end:%Y-%m-%d}"
        )

    # The next mahadasha is the single most-asked-about future fact, so it is
    # supplied rather than left for the model to work out from the sequence.
    maha = active[0]
    following = [p for p in timeline.periods if p.start >= maha.end]
    if following:
        nxt = following[0]
        lines.append(
            f"  next mahadasha: {nxt.lord} from {nxt.start:%Y-%m-%d}"
            f" ({nxt.duration_years:.0f} years)"
        )

    return "\n".join(lines)


def today_facts(sky: Panchang, sky_chart: Chart, natal: Chart) -> str:
    """The sky right now, set against the one this person was born under.

    Both halves matter and neither is the other: the first is true for everyone
    alive at this moment, the second is the only part that is theirs. Labelling
    them apart is what stops a daily line being written as though the sky were
    addressing one reader.
    """
    moon = sky_chart.grahas["Moon"]
    sun = sky_chart.grahas["Sun"]

    return "\n".join(
        [
            "TODAY  (the sky now, at the reader's place — the same for everyone)",
            f"  tithi: {sky.paksha} {sky.tithi} ({sky.tithi_percent:.0f}% elapsed)",
            f"  masa: {sky.masa}   Vikram Samvat {sky.vikram_samvat}",
            f"  vara: {sky.vara} (ruled by {sky.vara_lord})",
            f"  Moon: {moon.placement.rashi} — {moon.placement.nakshatra}"
            f" pada {moon.placement.pada}",
            f"  Sun: {sun.placement.rashi}",
            f"  yoga: {sky.yoga}   karana: {sky.karana}",
            "",
            "AGAINST THIS READER'S BIRTH",
            f"  birth Moon: {natal.moon_rashi} — {natal.janma_nakshatra}",
            f"  lagna: {natal.lagna.rashi}",
        ]
    )


def build_daily_brief(
    natal: Chart,
    sky: Panchang,
    sky_chart: Chart,
    timeline: VimshottariTimeline,
    as_of: dt.datetime,
) -> str:
    """The brief behind a daily line.

    Smaller than `build_brief` on purpose. A one-sentence tip handed the whole
    natal chart reaches for a placement to name, and a placement named in
    passing is the thing this product exists not to do. What it gets instead is
    the period the reader is in and the day everyone is in — which is all a
    daily line can honestly be about.
    """
    return "\n\n".join(
        [
            "=== COMPUTED DATA ===",
            today_facts(sky, sky_chart, natal),
            dasha_facts(timeline, as_of),
            "=== END COMPUTED DATA ===",
        ]
    )


def build_brief(
    chart: Chart,
    panchang: Panchang,
    timeline: VimshottariTimeline,
    as_of: dt.datetime,
) -> str:
    """The complete deterministic brief handed to the model.

    This is the model's entire factual world for the request. Anything it says
    that is not derivable from this block is, by definition, invented — which
    is what makes the grounding check in `grounding.py` meaningful.
    """
    return "\n\n".join(
        [
            "=== COMPUTED CHART DATA ===",
            chart_facts(chart),
            panchang_facts(panchang),
            dasha_facts(timeline, as_of),
            "=== END CHART DATA ===",
        ]
    )

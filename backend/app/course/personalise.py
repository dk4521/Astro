"""Chapter ideas, located in one reader's chart.

Every function here is arithmetic over data the engine already produced. None of
them call a model, none of them can be wrong in the way generated text can be
wrong, and all of them cost nothing per reader — which matters when free-tier
capacity is the app's scarcest resource.

Each returns text in both languages, or None when this particular chart has no
example of the idea. Returning None is a feature: a course that claims every
chart demonstrates every rule is teaching astrology badly.
"""

from __future__ import annotations

import datetime as dt

from ..astro import constants as K
from ..astro.chart import Chart
from ..astro.dasha import VimshottariTimeline
from ..astro.panchang import Panchang
from .models import Text


def _join(items: list[str], conjunction: str = "and") -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} {conjunction} {items[-1]}"


def _hi_graha(name: str) -> str:
    return K.GRAHA_HI.get(name, name)


def _hi_rashi(name: str) -> str:
    try:
        return K.RASHIS_HI[K.RASHIS.index(name)]
    except ValueError:
        return name


def _hi_verb(count: int) -> str:
    """`है` or `हैं`.

    Hindi agrees with number, so any sentence built from a joined list needs the
    plural once the list has more than one item. English gets this for free from
    "has"; Hindi does not.
    """
    return "है" if count == 1 else "हैं"


def _hi_nakshatra(name: str) -> str:
    try:
        return K.NAKSHATRAS_HI[K.NAKSHATRAS.index(name)]
    except ValueError:
        return name


def _hi_vara(name: str) -> str:
    try:
        return K.VARA_NAMES_HI[K.VARA_NAMES.index(name)]
    except ValueError:
        return name


def _hi_tithi(name: str) -> str:
    try:
        return K.TITHI_NAMES_HI[K.TITHI_NAMES.index(name)]
    except ValueError:
        return name


def _hi_yoga(name: str) -> str:
    try:
        return K.YOGA_NAMES_HI[K.YOGA_NAMES.index(name)]
    except ValueError:
        return name


# Gregorian months, because the dates the engine hands out are Gregorian. They
# live here rather than in `astro.constants`, which holds Vedic reference data.
_MONTHS_HI: tuple[str, ...] = (
    "जनवरी", "फ़रवरी", "मार्च", "अप्रैल", "मई", "जून",
    "जुलाई", "अगस्त", "सितंबर", "अक्तूबर", "नवंबर", "दिसंबर",
)


def _hi_month(when: dt.date) -> str:
    return f"{_MONTHS_HI[when.month - 1]} {when.year}"


def _hi_full_date(when: dt.date) -> str:
    return f"{when.day} {_MONTHS_HI[when.month - 1]} {when.year}"


def _hi_offset(chart: Chart) -> str:
    """The birth timezone as a UTC offset, written in Devanagari.

    The IANA name (`Asia/Kolkata`) is an identifier rather than a word, so there
    is nothing to translate. The offset is the part a reader can actually check
    against the clock time on a birth certificate, so the Hindi reading gives
    that instead.
    """
    # `birth_local` is naive local clock time; `birth_utc` is aware. Drop the
    # tzinfo before subtracting so the difference is the offset itself.
    naive_utc = chart.birth_utc.replace(tzinfo=None)
    minutes = round((chart.birth_local - naive_utc).total_seconds() / 60)
    sign = "+" if minutes >= 0 else "-"
    minutes = abs(minutes)
    return f"यूटीसी{sign}{minutes // 60:02d}:{minutes % 60:02d}"


def _hi_join(items: list[str]) -> str:
    if not items:
        return ""
    if len(items) == 1:
        return items[0]
    return f"{', '.join(items[:-1])} और {items[-1]}"


# Oblique: the form that precedes a postposition — "तीसरे भाव में".
HI_ORDINALS = [
    "", "पहले", "दूसरे", "तीसरे", "चौथे", "पाँचवें", "छठे",
    "सातवें", "आठवें", "नवें", "दसवें", "ग्यारहवें", "बारहवें",
]

# Nominative: the form that stands as the subject or complement — "भाव तीसरा है".
# Hindi inflects these; using the oblique form here reads as broken to a native
# reader even though English needs no such distinction.
HI_ORDINALS_NOM = [
    "", "पहला", "दूसरा", "तीसरा", "चौथा", "पाँचवाँ", "छठा",
    "सातवाँ", "आठवाँ", "नवाँ", "दसवाँ", "ग्यारहवाँ", "बारहवाँ",
]


def birth_moment(
    chart: Chart, panchang: Panchang, dasha: VimshottariTimeline, place: str | None = None
) -> Text | None:
    when = chart.birth_local.strftime("%d %B %Y, %H:%M")
    when_hi = f"{_hi_full_date(chart.birth_local)}, {chart.birth_local:%H:%M}"
    # The place name is the reader's own input and is left exactly as typed; only
    # the fallback, which the app supplies, has a Hindi form.
    where = place or "your birth place"
    where_hi = place or "आपके जन्मस्थान"
    return {
        "en": (
            f"Your chart was cast for {where} at {when} ({chart.timezone}). At that "
            f"moment {chart.lagna.rashi} was climbing over the eastern horizon, "
            f"which is why {chart.lagna.rashi} is your lagna."
        ),
        "hi": (
            f"आपकी कुंडली {where_hi} के लिए {when_hi} ({_hi_offset(chart)}) पर बनाई गई। "
            f"उस क्षण पूर्वी क्षितिज पर {_hi_rashi(chart.lagna.rashi)} चढ़ रहा था — "
            f"इसीलिए {_hi_rashi(chart.lagna.rashi)} आपका लग्न है।"
        ),
    }


def lagna_speed(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            f"Your lagna sits at {chart.lagna.dms} of {chart.lagna.rashi}. Had you "
            f"been born two hours earlier or later, it would almost certainly be a "
            f"different sign — and every house number in your chart would shift with it."
        ),
        "hi": (
            f"आपका लग्न {_hi_rashi(chart.lagna.rashi)} में {chart.lagna.dms} पर है। "
            f"जन्म दो घंटे आगे-पीछे होता तो लगभग निश्चित रूप से दूसरी राशि होती — "
            f"और उसके साथ कुंडली का हर भाव-क्रमांक बदल जाता।"
        ),
    }


def moon_rashi(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    moon = chart.grahas.get("Moon")
    if moon is None:
        return None
    p = moon.placement
    return {
        "en": (
            f"Your Moon is at {p.dms} of {p.rashi} ({p.rashi_en}), a sign ruled by "
            f"{p.rashi_lord}. In Indian usage that makes {p.rashi} your rashi — the "
            f"one you would be asked for by name."
        ),
        "hi": (
            f"आपका चंद्रमा {_hi_rashi(p.rashi)} में {p.dms} पर है, जिसके स्वामी "
            f"{_hi_graha(p.rashi_lord)} हैं। भारत में यही आपकी राशि कहलाती है — "
            f"नाम पूछे जाने पर यही बताई जाती है।"
        ),
    }


def ayanamsa(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            f"Your chart used an ayanamsa of {chart.ayanamsa:.4f}° "
            f"({chart.ayanamsa_name}). Subtract that from a Western chart's positions "
            f"and you get these — the same sky, measured from a different zero."
        ),
        "hi": (
            f"आपकी कुंडली में अयनांश {chart.ayanamsa:.4f}° "
            f"({K.AYANAMSA_NAMES_HI.get(chart.ayanamsa_name, chart.ayanamsa_name)}) "
            f"लगाया गया है। पाश्चात्य कुंडली की स्थितियों में से इतना घटा दें तो यही "
            f"आँकड़े मिलते हैं — आकाश वही, शून्य-बिंदु अलग।"
        ),
    }


def graha_positions(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    rows_en = [
        f"{g.graha} in {g.placement.rashi} (house {g.house})"
        for g in list(chart.grahas.values())[:4]
    ]
    rows_hi = [
        f"{_hi_graha(g.graha)} {_hi_rashi(g.placement.rashi)} में ({HI_ORDINALS[g.house]} भाव)"
        for g in list(chart.grahas.values())[:4]
    ]
    return {
        "en": "In your chart: " + _join(rows_en) + ". The chart screen lists all nine.",
        "hi": "आपकी कुंडली में: " + _hi_join(rows_hi) + "। बाक़ी सब कुंडली स्क्रीन पर हैं।",
    }


def luminaries(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    sun, moon = chart.grahas.get("Sun"), chart.grahas.get("Moon")
    if sun is None or moon is None:
        return None
    gap = int(round(abs(sun.placement.longitude - moon.placement.longitude))) % 360
    return {
        "en": (
            f"Your Sun is in {sun.placement.rashi} and your Moon in "
            f"{moon.placement.rashi}, about {gap}° apart. That gap is exactly what "
            f"the tithi measures — yours was {panchang.paksha} {panchang.tithi}."
        ),
        "hi": (
            f"आपका सूर्य {_hi_rashi(sun.placement.rashi)} में और चंद्रमा "
            f"{_hi_rashi(moon.placement.rashi)} में है, क़रीब {gap}° की दूरी पर। "
            f"तिथि यही दूरी नापती है — आपकी तिथि "
            f"{K.PAKSHA_HI.get(panchang.paksha, panchang.paksha)} "
            f"{_hi_tithi(panchang.tithi)} थी।"
        ),
    }


def _one_graha(name: str):
    def fn(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
        g = chart.grahas.get(name)
        if g is None:
            return None
        marks_en = [m for m, on in (("retrograde", g.retrograde), ("combust", g.combust)) if on]
        marks_hi = [m for m, on in (("वक्री", g.retrograde), ("अस्त", g.combust)) if on]
        tail_en = f", and it is {_join(marks_en)}" if marks_en else ""
        tail_hi = f", और यह {_hi_join(marks_hi)} है" if marks_hi else ""
        return {
            "en": (
                f"Your {name} is in {g.placement.rashi}, in house {g.house}, at "
                f"{g.placement.dms}{tail_en}. Its nakshatra is {g.placement.nakshatra}."
            ),
            "hi": (
                f"आपका {_hi_graha(name)} {_hi_rashi(g.placement.rashi)} में, "
                f"{HI_ORDINALS[g.house]} भाव में, {g.placement.dms} पर है{tail_hi}। "
                f"नक्षत्र {_hi_nakshatra(g.placement.nakshatra)} है।"
            ),
        }

    return fn


sun_moon = _one_graha("Sun")
mars_mercury = _one_graha("Mars")
jupiter_venus = _one_graha("Jupiter")
saturn = _one_graha("Saturn")


def nodes(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    rahu, ketu = chart.grahas.get("Rahu"), chart.grahas.get("Ketu")
    if rahu is None or ketu is None:
        return None
    return {
        "en": (
            f"Your Rahu is in {rahu.placement.rashi} (house {rahu.house}) and Ketu in "
            f"{ketu.placement.rashi} (house {ketu.house}) — opposite signs, six houses "
            f"apart, as they always are. You can check it: their longitudes differ by "
            f"exactly 180°."
        ),
        "hi": (
            f"आपका राहु {_hi_rashi(rahu.placement.rashi)} ({HI_ORDINALS[rahu.house]} भाव) "
            f"में और केतु {_hi_rashi(ketu.placement.rashi)} ({HI_ORDINALS[ketu.house]} भाव) "
            f"में है — हमेशा की तरह आमने-सामने। जाँच लीजिए: दोनों के देशांतर में ठीक 180° का अंतर है।"
        ),
    }


def marked_grahas(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    retro = [g.graha for g in chart.grahas.values() if g.retrograde and g.graha not in K.SHADOW_GRAHAS]
    combust = [g.graha for g in chart.grahas.values() if g.combust]
    if not retro and not combust:
        return {
            "en": (
                "Your chart has no retrograde or combust grahas apart from Rahu and "
                "Ketu, which are always retrograde by definition."
            ),
            "hi": (
                "राहु-केतु को छोड़कर आपकी कुंडली में कोई ग्रह वक्री या अस्त नहीं है — "
                "और वे दोनों परिभाषा से ही सदा वक्री रहते हैं।"
            ),
        }
    parts_en, parts_hi = [], []
    if retro:
        parts_en.append(f"{_join(retro)} retrograde")
        parts_hi.append(f"{_hi_join([_hi_graha(g) for g in retro])} वक्री")
    if combust:
        parts_en.append(f"{_join(combust)} combust")
        parts_hi.append(f"{_hi_join([_hi_graha(g) for g in combust])} अस्त")
    return {
        "en": f"Your chart has {_join(parts_en)} — a measured state with a coloured tag on the chart screen, and no verdict attached.",
        "hi": (
            f"आपकी कुंडली में {_hi_join(parts_hi)} {_hi_verb(len(retro) + len(combust))} — "
            f"कुंडली स्क्रीन पर रंगीन निशान के साथ एक नापी हुई स्थिति, कोई फ़ैसला नहीं।"
        ),
    }


def _house_occupants(chart: Chart, house: int) -> list[str]:
    return [g.graha for g in chart.grahas.values() if g.house == house]


def houses_from_lagna(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    first = _house_occupants(chart, 1)
    tenth = _house_occupants(chart, 10)
    if not first and not tenth:
        return {
            "en": (
                f"Your 1st and 10th houses are both empty of grahas, which is ordinary "
                f"— nine grahas cannot fill twelve houses. An empty house is read "
                f"through its lord: yours are {chart.house_lords[1]} and "
                f"{chart.house_lords[10]}."
            ),
            "hi": (
                f"आपके पहले और दसवें भाव में कोई ग्रह नहीं है, जो सामान्य बात है — "
                f"नौ ग्रह बारह भाव नहीं भर सकते। खाली भाव उसके स्वामी से पढ़ा जाता है: "
                f"यहाँ {_hi_graha(chart.house_lords[1])} और {_hi_graha(chart.house_lords[10])}।"
            ),
        }
    bits_en, bits_hi = [], []
    if first:
        bits_en.append(f"{_join(first)} in your 1st house")
        bits_hi.append(f"पहले भाव में {_hi_join([_hi_graha(g) for g in first])}")
    if tenth:
        bits_en.append(f"{_join(tenth)} in your 10th")
        bits_hi.append(f"दसवें भाव में {_hi_join([_hi_graha(g) for g in tenth])}")
    return {
        # No "both": either house can be the only one occupied, and the sentence
        # has to read correctly when it is.
        "en": f"Your chart has {_join(bits_en)} — counted from {chart.lagna.rashi}, your lagna.",
        "hi": (
            f"आपकी कुंडली में {_hi_join(bits_hi)} {_hi_verb(len(first) + len(tenth))} — "
            f"गिनती {_hi_rashi(chart.lagna.rashi)} लग्न से है।"
        ),
    }


def kendra_trikona(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    kendra = [g.graha for g in chart.grahas.values() if g.house in (1, 4, 7, 10)]
    trikona = [g.graha for g in chart.grahas.values() if g.house in (1, 5, 9)]
    return {
        "en": (
            f"In your chart the kendras (1, 4, 7, 10) hold "
            f"{_join(kendra) if kendra else 'no grahas'}, and the trikonas (1, 5, 9) hold "
            f"{_join(trikona) if trikona else 'none'}."
        ),
        "hi": (
            f"आपकी कुंडली में केंद्र (1, 4, 7, 10) में "
            f"{_hi_join([_hi_graha(g) for g in kendra]) if kendra else 'कोई ग्रह नहीं'}, "
            f"और त्रिकोण (1, 5, 9) में "
            f"{_hi_join([_hi_graha(g) for g in trikona]) if trikona else 'कोई नहीं'} "
            f"{_hi_verb(len(trikona) or 1)}।"
        ),
    }


def busiest_house(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    counts: dict[int, list[str]] = {}
    for g in chart.grahas.values():
        counts.setdefault(g.house, []).append(g.graha)
    house, occupants = max(counts.items(), key=lambda kv: len(kv[1]))
    if len(occupants) < 2:
        return None
    return {
        "en": (
            f"Your busiest house is the {house}th, holding {_join(occupants)}. A "
            f"cluster like this is the tradition's cue that the affairs of that house "
            f"carry unusual weight — a description of emphasis, not a promise."
        ),
        "hi": (
            f"आपकी कुंडली का सबसे भरा भाव {HI_ORDINALS_NOM[house]} है, जिसमें "
            f"{_hi_join([_hi_graha(g) for g in occupants])} हैं। इतने ग्रहों का एक साथ होना "
            f"परंपरा में उस भाव के विषयों पर ज़ोर बताता है — वादा नहीं, बल दिशा।"
        ),
    }


def house_lords(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    tenth_lord = chart.house_lords[10]
    where = chart.grahas.get(tenth_lord)
    if where is None:
        return None
    return {
        "en": (
            f"Your 10th house is {chart.houses[10]}, so its lord is {tenth_lord} — "
            f"and {tenth_lord} sits in your {where.house}th house. That link, lord to "
            f"location, is how an empty house still gets read."
        ),
        "hi": (
            f"आपका दसवाँ भाव {_hi_rashi(chart.houses[10])} है, तो उसके स्वामी "
            f"{_hi_graha(tenth_lord)} हुए — और वे आपके {HI_ORDINALS[where.house]} भाव में "
            f"बैठे हैं। स्वामी और स्थान की यही कड़ी खाली भाव को भी पढ़ने लायक़ बनाती है।"
        ),
    }


def janma_nakshatra(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            f"Your janma nakshatra is {chart.janma_nakshatra}, pada "
            f"{panchang.nakshatra_pada}, ruled by {dasha.janma_nakshatra_lord}. That one "
            f"fact set your entire dasha timeline."
        ),
        "hi": (
            f"आपका जन्म नक्षत्र {_hi_nakshatra(chart.janma_nakshatra)} है, पाद "
            f"{panchang.nakshatra_pada}, स्वामी {_hi_graha(dasha.janma_nakshatra_lord)}। "
            f"इसी एक तथ्य से आपकी पूरी दशा-श्रृंखला तय हुई।"
        ),
    }


def pada_navamsa(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    moon = chart.grahas.get("Moon")
    if moon is None:
        return None
    return {
        "en": (
            f"Your Moon is in pada {moon.placement.pada} of {moon.placement.nakshatra}, "
            f"which places it in {moon.placement.navamsa} in the navamsa — the "
            f"divisional chart traditionally read for marriage."
        ),
        "hi": (
            f"आपका चंद्रमा {_hi_nakshatra(moon.placement.nakshatra)} के "
            f"{moon.placement.pada} पाद में है, "
            f"जिससे नवांश में वह {_hi_rashi(moon.placement.navamsa)} में पड़ता है — "
            f"नवांश वही विभाग-कुंडली है जो विवाह के लिए देखी जाती है।"
        ),
    }


def dasha_now(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    active = dasha.at(dt.datetime.now(dt.timezone.utc))
    if not active:
        return None
    maha = active[0]
    antar = active[1] if len(active) > 1 else None
    tail_en = f", and inside it a {antar.lord} antardasha until {antar.end:%b %Y}" if antar else ""
    tail_hi = (
        f", और उसके भीतर {_hi_graha(antar.lord)} की अंतर्दशा {_hi_month(antar.end)} तक"
        if antar
        else ""
    )
    return {
        "en": (
            f"You are in a {maha.lord} mahadasha, {maha.start:%b %Y} to {maha.end:%b %Y}"
            f"{tail_en}. It began from {chart.janma_nakshatra}, with "
            f"{dasha.balance_years:.1f} years of that first period already elapsed at birth."
        ),
        "hi": (
            f"अभी आप {_hi_graha(maha.lord)} की महादशा में हैं, {_hi_month(maha.start)} से "
            f"{_hi_month(maha.end)} तक{tail_hi}। यह {_hi_nakshatra(chart.janma_nakshatra)} से "
            f"शुरू हुई, और जन्म के समय उस पहली दशा के {dasha.balance_years:.1f} वर्ष पहले ही "
            f"बीत चुके थे।"
        ),
    }


def dasha_balance(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    first = dasha.periods[0] if dasha.periods else None
    if first is None:
        return None
    return {
        "en": (
            f"Your timeline opens with {first.lord}, because {dasha.janma_nakshatra_lord} "
            f"rules {chart.janma_nakshatra}. Only {first.duration_years:.1f} years of it "
            f"remained at birth — the rest had run before you were born."
        ),
        "hi": (
            f"आपकी श्रृंखला {_hi_graha(first.lord)} से खुलती है, क्योंकि "
            f"{_hi_nakshatra(chart.janma_nakshatra)} के स्वामी "
            f"{_hi_graha(dasha.janma_nakshatra_lord)} हैं। "
            f"जन्म के समय उसमें केवल {first.duration_years:.1f} वर्ष बचे थे — बाक़ी पहले ही बीत चुका था।"
        ),
    }


def sub_periods(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    active = dasha.at(dt.datetime.now(dt.timezone.utc))
    if len(active) < 3:
        return None
    maha, antar, praty = active[0], active[1], active[2]
    return {
        "en": (
            f"Right now you are three levels deep: {maha.lord} mahadasha → "
            f"{antar.lord} antardasha → {praty.lord} pratyantardasha, the last running "
            f"to {praty.end:%d %b %Y}."
        ),
        "hi": (
            f"अभी आप तीन स्तर भीतर हैं: {_hi_graha(maha.lord)} महादशा → "
            f"{_hi_graha(antar.lord)} अंतर्दशा → {_hi_graha(praty.lord)} प्रत्यंतर्दशा, "
            f"जो {_hi_full_date(praty.end)} तक चलेगी।"
        ),
    }


def birth_panchang(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            f"You were born on a {panchang.vara} (ruled by {panchang.vara_lord}), in "
            f"{panchang.paksha} paksha, on {panchang.tithi} tithi — "
            f"{panchang.tithi_percent:.0f}% elapsed. Yoga {panchang.yoga}, karana "
            f"{panchang.karana}."
        ),
        "hi": (
            f"आपका जन्म {_hi_vara(panchang.vara)} को हुआ "
            f"(स्वामी {_hi_graha(panchang.vara_lord)}), "
            f"{K.PAKSHA_HI.get(panchang.paksha, panchang.paksha)} पक्ष, "
            f"{_hi_tithi(panchang.tithi)} तिथि — {panchang.tithi_percent:.0f}% बीत चुकी थी। "
            f"योग {_hi_yoga(panchang.yoga)}, "
            f"करण {K.KARANA_HI.get(panchang.karana, panchang.karana)}।"
        ),
    }


def navamsa_lagna(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            f"Your rashi lagna is {chart.lagna.rashi}; in the navamsa it becomes "
            f"{chart.lagna.navamsa}. Two charts, one birth — the divisional one is a "
            f"magnification, not a second opinion."
        ),
        "hi": (
            f"आपका राशि-लग्न {_hi_rashi(chart.lagna.rashi)} है; नवांश में वह "
            f"{_hi_rashi(chart.lagna.navamsa)} हो जाता है। दो कुंडलियाँ, एक ही जन्म — "
            f"विभाग-कुंडली आवर्धन है, दूसरी राय नहीं।"
        ),
    }


def nothing_is_a_verdict(chart: Chart, panchang: Panchang, dasha: VimshottariTimeline) -> Text | None:
    return {
        "en": (
            "Nothing in your chart is a verdict. Every number the app has shown you is "
            "a position — measured, reproducible, and that is all any of it claims."
        ),
        "hi": (
            "आपकी कुंडली में कुछ भी फ़ैसला नहीं है। ऐप ने जो भी संख्या दिखाई है वह एक "
            "स्थिति है — नापी हुई, दोहराई जा सकने वाली, और उसका दावा बस इतना ही है।"
        ),
    }

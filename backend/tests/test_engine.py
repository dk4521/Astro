"""Tests for the deterministic astrology engine.

The engine's whole value is that it is arithmetic, not opinion — so these tests
pin it against externally known charts and against the classical rules, not
against its own previous output.
"""

from __future__ import annotations

import datetime as dt

import pytest

from app.astro import build_chart, decompose, navamsa_chart, panchang_for, vimshottari
from app.astro import constants as K
from app.astro.chart import divisional_sign
from app.astro.panchang import _karana_name

# The 1947 Indian independence chart is the most widely published Indian
# nativity, so its values are a genuine external check.
INDEPENDENCE = dict(
    birth_local=dt.datetime(1947, 8, 15, 0, 0),
    latitude=28.6139,
    longitude=77.2090,
)


@pytest.fixture(scope="module")
def independence_chart():
    return build_chart(**INDEPENDENCE)


# --- Longitude decomposition ------------------------------------------------


def test_decompose_at_zero():
    p = decompose(0.0)
    assert p.rashi == "Mesha"
    assert p.nakshatra == "Ashwini"
    assert p.pada == 1
    assert p.degree_in_rashi == 0.0


def test_decompose_wraps_at_360():
    assert decompose(360.0).longitude == 0.0
    assert decompose(-1.0).rashi == "Meena"
    assert decompose(370.0).rashi == "Mesha"


def test_nakshatra_boundaries_are_exact():
    """Each nakshatra spans exactly 13°20', starting at Ashwini 0°.

    The probe sits 1e-6° (3.6 milliarcsec) inside the arc — well below any
    achievable ephemeris precision, but outside the boundary-snap window.
    """
    for i, name in enumerate(K.NAKSHATRAS):
        start = i * K.NAKSHATRA_ARC
        assert decompose(start).nakshatra == name
        assert decompose(start + K.NAKSHATRA_ARC - 1e-6).nakshatra == name


def test_pada_boundaries():
    """Four padas of 3°20' per nakshatra."""
    for pada in range(4):
        lon = pada * K.PADA_ARC + 0.01
        assert decompose(lon).pada == pada + 1
    # Last pada of Revati is the final pada of the zodiac.
    assert decompose(359.99).pada == 4
    assert decompose(359.99).nakshatra == "Revati"


def test_exact_arc_boundaries_land_in_the_later_arc():
    """Regression: 360/27 is not binary-representable.

    Naive `lon // (360 / 27)` floors exactly-on-boundary longitudes one arc too
    low — 40.0° is precisely three nakshatras but lands in Krittika instead of
    Rohini, which silently changes the Vimshottari lord.
    """
    assert decompose(40.0).nakshatra == "Rohini"
    assert decompose(80.0).nakshatra == "Punarvasu"
    assert decompose(120.0).nakshatra == "Magha"
    assert decompose(240.0).nakshatra == "Mula"
    assert decompose(320.0).nakshatra == "Purva Bhadrapada"


def test_boundary_snapping_keeps_sign_and_degree_consistent():
    """A snapped index must not disagree with the reported degree."""
    for lon in (0.0, 30.0, 40.0, 120.0, 359.9999999999, 360.0):
        p = decompose(lon)
        assert 0.0 <= p.degree_in_rashi < 30.0
        assert p.rashi == K.RASHIS[p.rashi_index]
        # The degree must reconstruct the longitude it came from.
        assert (p.rashi_index * 30.0 + p.degree_in_rashi) == pytest.approx(
            p.longitude, abs=1e-9
        )


def test_rashi_lords_follow_classical_assignment():
    assert decompose(0.0).rashi_lord == "Mars"        # Mesha
    assert decompose(95.0).rashi_lord == "Moon"       # Karka
    assert decompose(125.0).rashi_lord == "Sun"       # Simha
    assert decompose(300.0).rashi_lord == "Saturn"    # Kumbha


def test_nakshatra_lords_cycle_in_vimshottari_order():
    assert K.NAKSHATRA_LORDS[0] == "Ketu"        # Ashwini
    assert K.NAKSHATRA_LORDS[8] == "Mercury"     # Ashlesha
    assert K.NAKSHATRA_LORDS[9] == "Ketu"        # Magha restarts the cycle
    assert len(K.NAKSHATRA_LORDS) == 27


def test_dms_formatting():
    assert decompose(0.0).dms == "0°00'00\""
    # 7.7325° -> 7°43'57"
    assert decompose(30.0 + 7.7325).dms == "7°43'57\""


# --- Navamsa ----------------------------------------------------------------


@pytest.mark.parametrize(
    "rashi_index,expected_first_navamsa",
    [
        (0, "Mesha"),       # Mesha, chara -> starts at itself
        (1, "Makara"),      # Vrishabha, sthira -> starts at the 9th
        (2, "Tula"),        # Mithuna, dwiswabhava -> starts at the 5th
        (3, "Karka"),       # Karka, chara
        (4, "Mesha"),       # Simha, sthira -> 9th from Simha is Mesha
        (5, "Makara"),      # Kanya, dwiswabhava
    ],
)
def test_navamsa_matches_classical_starting_rule(rashi_index, expected_first_navamsa):
    """The continuous-arc rule must reproduce chara/sthira/dwiswabhava starts.

    Classical rule: movable signs start their navamsa series at themselves,
    fixed signs at the 9th from themselves, dual signs at the 5th.
    """
    lon = rashi_index * 30.0 + 0.5
    assert decompose(lon).navamsa == expected_first_navamsa


def test_navamsa_advances_one_sign_per_arc():
    base = 0.0
    for step in range(9):
        lon = base + step * K.NAVAMSA_ARC + 0.01
        assert decompose(lon).navamsa_index == step % 12


def test_divisional_sign_d1_is_the_rashi():
    for lon in (0.0, 45.0, 123.4, 359.9):
        assert divisional_sign(lon, 1) == decompose(lon).rashi_index


def test_divisional_sign_d9_matches_decompose():
    for lon in (0.0, 45.0, 123.4, 359.9):
        assert divisional_sign(lon, 9) == decompose(lon).navamsa_index


def test_divisional_sign_rejects_zero():
    with pytest.raises(ValueError):
        divisional_sign(10.0, 0)


# --- Known chart ------------------------------------------------------------


def test_independence_chart_lagna(independence_chart):
    """Vrishabha lagna is the defining feature of this published chart."""
    assert independence_chart.lagna.rashi == "Vrishabha"
    assert independence_chart.lagna.degree_in_rashi == pytest.approx(7.73, abs=0.1)


def test_independence_chart_luminaries(independence_chart):
    grahas = independence_chart.grahas
    assert grahas["Moon"].placement.rashi == "Karka"
    assert grahas["Moon"].placement.nakshatra == "Pushya"
    assert grahas["Sun"].placement.rashi == "Karka"
    assert grahas["Rahu"].placement.rashi == "Vrishabha"
    assert grahas["Ketu"].placement.rashi == "Vrishchika"


def test_independence_chart_ayanamsa(independence_chart):
    """Lahiri ayanamsa was ~23°07' in 1947."""
    assert independence_chart.ayanamsa == pytest.approx(23.125, abs=0.01)


def test_timezone_resolved_from_coordinates(independence_chart):
    assert independence_chart.timezone == "Asia/Kolkata"
    # 00:00 IST is 18:30 UTC the previous day.
    assert independence_chart.birth_utc == dt.datetime(
        1947, 8, 14, 18, 30, tzinfo=dt.timezone.utc
    )


def test_houses_are_whole_sign_from_lagna(independence_chart):
    lagna_index = independence_chart.lagna.rashi_index
    for house in range(1, 13):
        expected = K.RASHIS[(lagna_index + house - 1) % 12]
        assert independence_chart.houses[house] == expected

    for graha in independence_chart.grahas.values():
        offset = (graha.placement.rashi_index - lagna_index) % 12
        assert graha.house == offset + 1


def test_ketu_is_always_opposite_rahu(independence_chart):
    rahu = independence_chart.grahas["Rahu"].placement.longitude
    ketu = independence_chart.grahas["Ketu"].placement.longitude
    assert (ketu - rahu) % 360.0 == pytest.approx(180.0, abs=1e-9)


def test_nodes_are_always_retrograde(independence_chart):
    assert independence_chart.grahas["Rahu"].retrograde
    assert independence_chart.grahas["Ketu"].retrograde


def test_sun_is_never_combust(independence_chart):
    assert not independence_chart.grahas["Sun"].combust


# Sidereal longitudes recorded from the Swiss Ephemeris implementation this
# engine replaced. They are an independent reference: two different ephemeris
# libraries, two different ayanamsa code paths, same answer.
SWISSEPH_REFERENCE = {
    "Sun": 117.9890,
    "Moon": 93.9835,
    "Mars": 67.4562,
    "Mercury": 103.6743,
    "Jupiter": 205.8777,
    "Venus": 112.5612,
    "Saturn": 110.4730,
}
SWISSEPH_REFERENCE_LAGNA = 37.73227002311478
SWISSEPH_REFERENCE_RAHU = 35.0697


def _arcsec_apart(a: float, b: float) -> float:
    return abs((a - b + 180.0) % 360.0 - 180.0) * 3600.0


def test_matches_swiss_ephemeris_reference(independence_chart):
    """Positions must still agree with the implementation this replaced."""
    for graha, expected in SWISSEPH_REFERENCE.items():
        actual = independence_chart.grahas[graha].placement.longitude
        assert _arcsec_apart(actual, expected) < 2.0, graha

    assert _arcsec_apart(independence_chart.lagna.longitude, SWISSEPH_REFERENCE_LAGNA) < 1.0


def test_mean_node_stays_within_its_known_tolerance(independence_chart):
    """Rahu uses Meeus' mean node; Swiss Ephemeris adds small periodic terms.

    The gap is bounded at roughly 19" — far inside a 12000" pada, but wide
    enough that it deserves an explicit bound rather than silent drift.
    """
    rahu = independence_chart.grahas["Rahu"].placement.longitude
    assert _arcsec_apart(rahu, SWISSEPH_REFERENCE_RAHU) < 20.0


def test_sidereal_conversion_accounts_for_nutation():
    """Regression: apparent longitudes need ayanamsa *plus* nutation removed.

    Apparent positions are referred to the true equinox of date, the ayanamsa
    to the mean equinox. Subtracting the bare mean ayanamsa leaves every graha
    displaced by the nutation in longitude — up to 17", identical for all of
    them, which reads as a plausible chart rather than an error.
    """
    from app.astro import ephemeris as E

    jd = E.julian_day(dt.datetime(1947, 8, 14, 18, 30, tzinfo=dt.timezone.utc))
    t = E._load_kernel()[0].ut1_jd(jd)

    mean = E._mean_ayanamsa(jd)
    effective = E._effective_ayanamsa(jd, t)

    # They must differ, and only by the nutation in longitude.
    assert mean != effective
    assert (effective - mean) == pytest.approx(E._nutation_longitude(t), abs=1e-12)
    # Nutation in longitude never exceeds ~17.3".
    assert abs(effective - mean) * 3600.0 < 20.0


def test_reported_ayanamsa_is_the_mean_value(independence_chart):
    """The published Lahiri value for 1947 is ~23°07'30"."""
    assert independence_chart.ayanamsa == pytest.approx(23.125451, abs=1e-5)


def test_engine_is_deterministic():
    """Same input, byte-identical output — the product depends on this."""
    a = build_chart(**INDEPENDENCE)
    b = build_chart(**INDEPENDENCE)
    assert a.julian_day == b.julian_day
    assert a.lagna == b.lagna
    assert a.grahas == b.grahas


def test_chart_is_identical_when_computed_on_a_worker_thread():
    """FastAPI runs sync endpoints in a threadpool, so charts must be thread-safe.

    This guards a failure mode the engine has already been bitten by once: the
    previous `pyswisseph` backend kept its configuration in thread-local
    storage, so worker threads silently computed with Fagan-Bradley instead of
    Lahiri — ~0.88° out, enough to move grahas between nakshatras and change
    the dasha lord, with nothing raised. Skyfield holds no such state, but a
    future ephemeris swap could reintroduce it.
    """
    import concurrent.futures

    reference = build_chart(**INDEPENDENCE)

    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        results = [
            future.result()
            for future in [
                pool.submit(build_chart, **INDEPENDENCE) for _ in range(4)
            ]
        ]

    for chart in results:
        assert chart.ayanamsa == pytest.approx(reference.ayanamsa, abs=1e-12)
        assert chart.lagna == reference.lagna
        assert chart.grahas == reference.grahas


def test_navamsa_chart_covers_every_body(independence_chart):
    d9 = navamsa_chart(independence_chart)
    assert set(d9) == set(K.GRAHAS) | {"Ascendant"}
    assert all(sign in K.RASHIS for sign in d9.values())


def test_rejects_out_of_range_coordinates():
    with pytest.raises(ValueError):
        build_chart(dt.datetime(2000, 1, 1), 95.0, 0.0)
    with pytest.raises(ValueError):
        build_chart(dt.datetime(2000, 1, 1), 0.0, 200.0)


def test_rejects_timezone_aware_birth_time():
    with pytest.raises(ValueError):
        build_chart(
            dt.datetime(2000, 1, 1, tzinfo=dt.timezone.utc), 28.6, 77.2
        )


def test_historical_timezone_offsets_are_honoured():
    """India used +06:30 during part of WWII; tzdata must be respected."""
    wartime = build_chart(dt.datetime(1944, 6, 1, 12, 0), 22.5726, 88.3639)
    assert wartime.birth_utc.hour == 5
    assert wartime.birth_utc.minute == 30

    modern = build_chart(dt.datetime(2000, 6, 1, 12, 0), 22.5726, 88.3639)
    assert modern.birth_utc.hour == 6
    assert modern.birth_utc.minute == 30


# --- Vimshottari dasha ------------------------------------------------------


def test_vimshottari_total_is_120_years():
    assert sum(K.VIMSHOTTARI_YEARS.values()) == K.VIMSHOTTARI_TOTAL_YEARS


def test_first_mahadasha_lord_is_janma_nakshatra_lord(independence_chart):
    timeline = vimshottari(independence_chart)
    assert timeline.janma_nakshatra == "Pushya"
    assert timeline.janma_nakshatra_lord == "Saturn"
    assert timeline.periods[0].lord == "Saturn"


def test_dasha_balance_at_birth(independence_chart):
    """Published balance for this chart is Saturn ~18 years."""
    timeline = vimshottari(independence_chart)
    assert timeline.balance_years == pytest.approx(18.07, abs=0.05)


def test_first_mahadasha_brackets_the_birth_moment(independence_chart):
    """The first period starts before birth by the elapsed portion."""
    timeline = vimshottari(independence_chart)
    first = timeline.periods[0]
    assert first.start < independence_chart.birth_utc < first.end

    elapsed_years = (
        independence_chart.birth_utc - first.start
    ).days / K.DAYS_PER_YEAR
    assert elapsed_years + timeline.balance_years == pytest.approx(
        K.VIMSHOTTARI_YEARS["Saturn"], abs=0.01
    )


def test_mahadasha_durations_match_the_table(independence_chart):
    timeline = vimshottari(independence_chart, levels=1)
    for period in timeline.periods:
        assert period.duration_years == pytest.approx(
            K.VIMSHOTTARI_YEARS[period.lord], abs=1e-6
        )


def test_mahadashas_follow_vimshottari_order(independence_chart):
    timeline = vimshottari(independence_chart, levels=1)
    lords = [p.lord for p in timeline.periods]
    start = K.VIMSHOTTARI_ORDER.index("Saturn")
    expected = [K.VIMSHOTTARI_ORDER[(start + i) % 9] for i in range(9)]
    assert lords == expected


def test_periods_are_contiguous(independence_chart):
    timeline = vimshottari(independence_chart)
    for previous, following in zip(timeline.periods, timeline.periods[1:]):
        assert previous.end == following.start


def test_subperiods_exactly_fill_their_parent(independence_chart):
    timeline = vimshottari(independence_chart, levels=3)
    for maha in timeline.periods:
        assert len(maha.children) == 9
        assert maha.children[0].start == maha.start
        assert maha.children[-1].end == maha.end
        # First antardasha of a mahadasha is ruled by the mahadasha lord.
        assert maha.children[0].lord == maha.lord

        for antar in maha.children:
            assert len(antar.children) == 9
            assert antar.children[0].start == antar.start
            assert antar.children[-1].end == antar.end


def test_antardasha_proportions(independence_chart):
    """An antardasha takes the same share of its parent as of the 120 years."""
    timeline = vimshottari(independence_chart, levels=2)
    maha = timeline.periods[0]
    for antar in maha.children:
        share = K.VIMSHOTTARI_YEARS[antar.lord] / K.VIMSHOTTARI_TOTAL_YEARS
        assert antar.duration_days == pytest.approx(
            maha.duration_days * share, rel=1e-9
        )


def test_lookup_returns_nested_active_periods(independence_chart):
    timeline = vimshottari(independence_chart, levels=3)
    moment = dt.datetime(1990, 1, 1, tzinfo=dt.timezone.utc)
    active = timeline.at(moment)

    assert len(active) == 3
    assert [p.level for p in active] == [1, 2, 3]
    for period in active:
        assert period.contains(moment)


def test_lookup_outside_timeline_is_empty(independence_chart):
    timeline = vimshottari(independence_chart, levels=1)
    assert timeline.at(dt.datetime(1800, 1, 1, tzinfo=dt.timezone.utc)) == []
    assert timeline.at(dt.datetime(2500, 1, 1, tzinfo=dt.timezone.utc)) == []


def test_levels_argument_is_validated(independence_chart):
    with pytest.raises(ValueError):
        vimshottari(independence_chart, levels=0)
    with pytest.raises(ValueError):
        vimshottari(independence_chart, levels=4)


# --- Panchang ---------------------------------------------------------------


def test_panchang_of_known_chart(independence_chart):
    p = panchang_for(independence_chart)
    assert p.paksha == "Krishna"
    assert p.tithi == "Trayodashi"
    assert p.nakshatra == "Pushya"
    # The Vedic day turns at sunrise, so midnight on Friday 15 Aug still
    # belongs to Thursday's vara.
    assert p.vara == "Guruvara"
    assert p.vara_lord == "Jupiter"


def test_new_moon_is_first_tithi_of_shukla():
    """At conjunction the tithi index resets to Shukla Pratipada."""
    from app.astro.panchang import TITHI_ARC

    assert int(0.0 // TITHI_ARC) == 0
    assert K.TITHI_NAMES[0] == "Pratipada"


def test_karana_sequence():
    """Four fixed karanas bracket eight cycles of the seven movable ones."""
    assert _karana_name(0) == "Kimstughna"
    assert _karana_name(1) == "Bava"
    assert _karana_name(7) == "Vishti"
    assert _karana_name(8) == "Bava"       # cycle restarts
    assert _karana_name(56) == "Vishti"    # eighth and final movable cycle ends
    assert _karana_name(57) == "Shakuni"
    assert _karana_name(58) == "Chatushpada"
    assert _karana_name(59) == "Naga"


def test_every_karana_index_is_named():
    names = {_karana_name(i) for i in range(60)}
    assert names == set(_MOVABLE := set(
        ("Bava", "Balava", "Kaulava", "Taitila", "Gara", "Vanija", "Vishti")
    )) | {"Kimstughna", "Shakuni", "Chatushpada", "Naga"}


def test_tithi_and_yoga_indices_stay_in_range():
    """Sweep a year of charts and confirm no index ever escapes its table."""
    for day in range(0, 365, 7):
        moment = dt.datetime(2024, 1, 1) + dt.timedelta(days=day)
        chart = build_chart(moment, 28.6139, 77.2090)
        p = panchang_for(chart)
        assert 0 <= p.tithi_index < 30
        assert 0 <= p.yoga_index < 27
        assert 0 <= p.karana_index < 60
        assert p.vara in K.VARA_NAMES

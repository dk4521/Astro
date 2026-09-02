"""Tests for the tarot feature.

No API key and no network. What is worth asserting here is not that a deck of
cards works — it is the three claims the feature actually makes:

  the seed *is* the shuffle, so a spread can be reproduced by anyone, forever;
  the deck is written material, complete in both languages, and stays 78 cards;
  a generated reading is checked against the hand that was dealt, and against
  the rule that a tarot reading contains no astrology at all.

The pinned-hand test below is the one that will fail one day, and it is meant
to. Reordering the deck or moving `sample` after the orientation coin changes
every seed ever issued — including seeds a reader has saved. That should be a
loud decision, not a quiet diff.
"""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from app import auth, tarot
from app.ai import grounding, set_client
from app.ai.client import Request
from app.api import routes as api_routes
from app.main import app
from app.tarot import deck, reading, spread
from app.tarot import grounding as card_grounding

client = TestClient(app)


class StubClient:
    """Records the request it was given and replies with canned text."""

    def __init__(self, reply: str = "Three cards, read plainly.") -> None:
        self.reply = reply
        self.requests: list[Request] = []

    def complete(self, request: Request) -> str:
        self.requests.append(request)
        return self.reply

    def stream(self, request: Request):
        self.requests.append(request)
        yield self.reply


@pytest.fixture
def stub():
    installed = StubClient()
    set_client(installed)
    yield installed
    set_client(None)


# --- The deck ---------------------------------------------------------------


def test_the_deck_is_seventy_eight_cards():
    assert len(deck.CARDS) == 78
    assert len({card.id for card in deck.CARDS}) == 78


def test_the_deck_is_twenty_two_major_and_four_suits_of_fourteen():
    major = [card for card in deck.CARDS if card.arcana == "major"]
    assert len(major) == 22
    assert sorted(card.number for card in major) == list(range(22))

    for suit in deck.SUITS:
        cards = [card for card in deck.CARDS if card.suit == suit.id]
        assert len(cards) == 14, suit.id
        assert sorted(card.number for card in cards) == list(range(1, 15))


def test_every_card_is_written_in_both_languages():
    """A missing Hindi line would fall back to English and never be noticed."""
    for card in deck.CARDS:
        for field in (card.name, card.keywords, card.upright, card.reversed):
            for language in deck.LANGUAGES:
                assert field.get(language, "").strip(), f"{card.id} has no {language}"


def test_minor_names_are_composed_with_the_grammar_hindi_needs():
    """Fifty-six names written by hand would drift; composed ones cannot.

    The particle is the part a list gets wrong: रानी is feminine and takes की,
    while राजा, शिष्य and अश्वारोही take का.
    """
    by_id = deck.CARDS_BY_ID
    assert by_id["swords-three"].name == {"en": "Three of Swords", "hi": "तीन तलवारें"}
    assert by_id["swords-queen"].name["hi"] == "तलवारों की रानी"
    assert by_id["swords-king"].name["hi"] == "तलवारों का राजा"
    assert by_id["cups-ace"].name["hi"] == "प्यालों का इक्का"
    assert by_id["wands-ten"].name["hi"] == "दस छड़ियाँ"


def test_no_card_is_described_as_a_warning():
    """The one house rule the deck exists to keep.

    Every tarot product on the market sells Death, the Tower and the Ten of
    Swords as bad news. Checking the words is crude, but it fails loudly the
    day someone writes "beware" into a card that people already arrive
    frightened of.
    """
    forbidden = ("beware", "danger", "warning", "curse", "unlucky", "doomed",
                 "सावधान", "ख़तरा", "खतरा", "चेतावनी", "अशुभ", "श्राप")
    for card in deck.CARDS:
        for field in (card.upright, card.reversed, card.keywords):
            for text in field.values():
                lowered = text.lower()
                for word in forbidden:
                    assert word not in lowered, f"{card.id}: {text!r}"


# --- The draw ---------------------------------------------------------------


def test_the_same_seed_deals_the_same_hand():
    first = spread.draw("enumasky-test")
    second = spread.draw("enumasky-test")
    assert first == second


def test_a_pinned_seed_still_deals_the_hand_it_always_did():
    """The seed is a promise made to readers, so it is pinned here.

    If this fails, the deck's order or the order of the random calls in
    `draw()` changed — and every spread anyone saved now deals different cards.
    Update this test only together with a decision to break that promise.
    """
    drawn = spread.draw("abc123")
    assert [item.card.id for item in drawn.cards] == [
        "major-empress",
        "wands-king",
        "pentacles-ten",
    ]
    assert [item.reversed for item in drawn.cards] == [False, False, True]


def test_a_seedless_draw_returns_the_seed_it_used():
    drawn = spread.draw()
    assert drawn.seed
    assert spread.draw(drawn.seed) == drawn


def test_two_fresh_draws_differ():
    seeds = {spread.draw().seed for _ in range(20)}
    assert len(seeds) == 20


def test_a_spread_never_deals_the_same_card_twice():
    for index in range(200):
        drawn = spread.draw(f"seed-{index}")
        assert len({item.card.id for item in drawn.cards}) == 3


def test_the_positions_are_situation_obstacle_advice():
    """Not past / present / future — the spread is the product's position.

    A timeline spread is a forecast, and this app does not forecast. Asserting
    the ids keeps that from being quietly swapped for the more marketable one.
    """
    assert [position.id for position in spread.POSITIONS] == [
        "situation",
        "obstacle",
        "advice",
    ]


def test_cards_come_up_both_ways_round():
    reversals = [
        item.reversed for index in range(150) for item in spread.draw(f"s{index}").cards
    ]
    assert 0.35 < sum(reversals) / len(reversals) < 0.65


def test_the_brief_carries_the_meanings_and_nothing_invented():
    drawn = spread.draw("abc123")
    text = spread.brief(drawn, "should I take the job?", "en")

    for item in drawn.cards:
        assert item.card.name["en"] in text
        assert item.meaning("en") in text
    assert "should I take the job?" in text
    assert drawn.seed in text


def test_a_hindi_brief_carries_the_hindi_meanings():
    """A Hindi reading built from English source lines reads like a translation."""
    drawn = spread.draw("abc123")
    text = spread.brief(drawn, None, "hi")
    assert drawn.cards[0].meaning("hi") in text
    assert "none asked" in text


# --- Checking a reading -----------------------------------------------------


def test_a_card_that_was_not_dealt_is_caught():
    drawn = spread.draw("abc123")  # Empress, King of Wands, Ten of Pentacles
    findings = card_grounding.check("The Tower says this will not hold.", drawn)
    assert [finding.card_id for finding in findings] == ["major-tower"]


def test_the_cards_that_were_dealt_are_not_caught():
    drawn = spread.draw("abc123")
    assert card_grounding.check(
        "The Empress and the King of Wands, with the Ten of Pentacles reversed.", drawn
    ) == []


def test_ordinary_words_are_not_mistaken_for_cards():
    """A checker that cries wolf gets switched off, so this one stays quiet.

    Half the major arcana are ordinary words. Lowercase English is prose, and
    the names that survive no case distinction at all are not matched in Hindi.
    """
    drawn = spread.draw("abc123")
    assert card_grounding.check("an ending, not a death; the sun is out", drawn) == []
    assert card_grounding.check("संसार में तारा दिखा, यह उनकी दशा है", drawn) == []


def test_a_hindi_card_name_is_caught():
    drawn = spread.draw("abc123")
    findings = card_grounding.check("मीनार गिरने को है।", drawn)
    assert [finding.card_id for finding in findings] == ["major-tower"]


def test_every_skipped_card_id_is_a_real_card():
    """A renamed card would leave a stale id and switch the check off silently."""
    for card_id in card_grounding._SKIP_HI | card_grounding._SKIP_EN:
        assert card_id in deck.CARDS_BY_ID


def test_astrology_in_a_tarot_reading_is_caught():
    assert grounding.mentions_chart("Your Saturn dasha is running.") == ["dasha", "Saturn"]
    assert grounding.mentions_chart("आपकी कुंडली में शनि") == ["कुंडली", "शनि"]


def test_the_sun_and_the_moon_are_cards_here_not_grahas():
    """Flagging them would make the check fire on a correct reading of The Moon."""
    assert grounding.mentions_chart("The Moon, reversed, and The Sun after it.") == []


def test_ordinary_hindi_is_not_mistaken_for_astrology():
    """राशि is a sum of money and दशा is a state; a Pentacles reading uses both."""
    assert grounding.mentions_chart("एक छोटी राशि बचाइए; दशा सुधरेगी") == []


# --- The reading ------------------------------------------------------------


def test_a_reading_is_grounded_when_it_names_only_what_was_dealt(stub):
    drawn = spread.draw("abc123")
    stub.reply = "The Empress is tending something that is nearly ready."
    result = reading.interpret(drawn, "how is work going?", "en")

    assert result.model_grounded
    assert result.contradictions == []


def test_a_reading_that_invents_a_card_is_not_grounded(stub):
    drawn = spread.draw("abc123")
    stub.reply = "The Tower is here, so nothing will hold."
    result = reading.interpret(drawn, None, "en")

    assert not result.model_grounded
    assert "major-tower" in " ".join(result.contradictions) or "The Tower" in " ".join(
        result.contradictions
    )


def test_a_reading_that_reaches_for_the_chart_is_not_grounded(stub):
    """The system prompt calls itself a Vedic astrology app; this measures the fix."""
    drawn = spread.draw("abc123")
    stub.reply = "The Empress, and your Saturn dasha, both say the same thing."
    result = reading.interpret(drawn, None, "en")

    assert not result.model_grounded
    assert any("astrology" in line for line in result.contradictions)


def test_an_ungrounded_reading_is_never_cached(stub):
    """One bad reading must not become the same bad reading all day."""
    drawn = spread.draw("abc123")
    stub.reply = "The Tower is here."
    reading.interpret(drawn, None, "en")
    reading.interpret(drawn, None, "en")

    assert len(stub.requests) == 2


def test_the_same_spread_and_question_is_asked_once(stub):
    drawn = spread.draw("abc123")
    first = reading.interpret(drawn, "what now?", "en")
    second = reading.interpret(drawn, "what now?", "en")

    assert len(stub.requests) == 1
    assert second.cached and not first.cached


def test_the_model_is_handed_the_cards_and_the_tarot_rules(stub):
    drawn = spread.draw("abc123")
    reading.interpret(drawn, "what now?", "en")

    sent = stub.requests[0]
    assert "The Empress" in sent.messages[0]["content"]
    assert "no dasha" in sent.suffix and "not a chart" in sent.suffix


# --- The HTTP surface -------------------------------------------------------


def test_the_deck_endpoint_returns_the_whole_deck():
    response = client.get("/v1/tarot/deck")
    assert response.status_code == 200

    body = response.json()
    assert len(body["cards"]) == 78
    assert len(body["suits"]) == 4
    # Cacheable: card text is prose, and prose gets corrected.
    assert "max-age" in response.headers.get("Cache-Control", "")


def test_a_draw_is_free_and_reproducible():
    first = client.post("/v1/tarot/draw", json={})
    assert first.status_code == 200

    body = first.json()
    assert [card["position"]["id"] for card in body["cards"]] == [
        "situation",
        "obstacle",
        "advice",
    ]

    again = client.post("/v1/tarot/draw", json={"seed": body["seed"]}).json()
    assert again == body


def test_a_drawn_card_carries_the_line_for_the_way_it_came_up():
    body = client.post("/v1/tarot/draw", json={"seed": "abc123"}).json()
    advice = body["cards"][2]

    assert advice["reversed"] is True
    assert advice["meaning"] == tarot.CARDS_BY_ID["pentacles-ten"].reversed["en"]
    assert advice["meaning_hi"] == tarot.CARDS_BY_ID["pentacles-ten"].reversed["hi"]


def test_a_nonsense_seed_is_refused_rather_than_hashed():
    assert client.post("/v1/tarot/draw", json={"seed": "../../etc/passwd"}).status_code == 422


def test_the_reading_endpoint_deals_from_the_seed_not_from_the_client(stub, monkeypatch):
    """A client cannot get a reading of a spread it made up."""
    monkeypatch.setattr(api_routes.entitlements, "is_configured", lambda: False)
    response = client.post(
        "/v1/tarot/reading",
        json={"seed": "abc123", "question": "what now?", "language": "en",
              "cards": ["major-tower"]},
    )
    assert response.status_code == 200

    sent = stub.requests[0].messages[0]["content"]
    assert "The Empress" in sent and "The Tower" not in sent


def test_a_reading_needs_a_subscription(stub, monkeypatch):
    """The gate is the entitlement now, and it is checked on the server."""
    monkeypatch.setattr(api_routes.entitlements, "is_configured", lambda: True)
    monkeypatch.setattr(
        api_routes.entitlements,
        "entitlement_of",
        lambda uid: api_routes.entitlements.Entitlement(active=True),
    )
    # Overridden rather than monkeypatched: the route captured the real
    # dependency at import, so rebinding the module attribute would leave the
    # override keyed on a function nothing depends on.
    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(
        id="user-1", email=None
    )

    try:
        response = client.post("/v1/tarot/reading", json={"seed": "abc123"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 200
    assert "balance" not in response.json()


def test_a_reader_without_a_subscription_is_sent_to_the_paywall(stub, monkeypatch):
    """402, not 401 and not 403: the app opens the plans screen on this one."""
    monkeypatch.setattr(api_routes.entitlements, "is_configured", lambda: True)
    monkeypatch.setattr(
        api_routes.entitlements,
        "entitlement_of",
        lambda uid: api_routes.entitlements.NOT_ENTITLED,
    )
    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(
        id="user-1", email=None
    )

    try:
        response = client.post("/v1/tarot/reading", json={"seed": "abc123"})
    finally:
        app.dependency_overrides.clear()

    assert response.status_code == 402
    assert stub.requests == []  # the model was never asked


def test_turning_the_cards_over_stays_free(monkeypatch):
    """Nobody should have to subscribe to look at three cards."""
    monkeypatch.setattr(api_routes.entitlements, "is_configured", lambda: True)
    assert client.post("/v1/tarot/draw", json={"seed": "abc123"}).status_code == 200
    assert client.get("/v1/tarot/deck").status_code == 200


def test_signing_in_is_required_once_billing_is_on(stub, monkeypatch):
    """401 means sign in; 402 means subscribe. Two screens, two statuses."""
    monkeypatch.setattr(api_routes.entitlements, "is_configured", lambda: True)
    response = client.post("/v1/tarot/reading", json={"seed": "abc123"})
    assert response.status_code == 401

"""Tests for the paid path, after credits.

Nothing here talks to RevenueCat or Supabase. What is worth testing is not that
those services work — it is the seam either side of them.

The failures these are written against, all of which were once shipped and none
of which are visible by reading the happy path:

  an endpoint that calls a model without asking who is calling
  a gate that answers 402 and 401 with the same status, so the app guesses
  a paywall that opens when the payment service is merely unreachable
  an entitlement that expired but is still listed, and reads as active
  no ceiling at all on how fast any of it can be asked for

The last one has a history worth keeping. The old ledger metered messages with
an idempotency key the client chose, and answered a repeat with "already paid" —
so one fixed `request_id`, sent forever, cost exactly one credit ever. There is
no key to repeat now, and `test_a_client_cannot_replay_its_way_past_the_gate`
is the regression that says the shape of that bug did not survive the rewrite.
"""

from __future__ import annotations

import datetime as dt

import httpx
import pytest
from fastapi.testclient import TestClient

from app import auth, entitlements, ratelimit
from app.ai.client import set_client
from app.main import app

client = TestClient(app)

BIRTH = {
    "date": "1995-03-14",
    "time": "07:42",
    "latitude": 28.6139,
    "longitude": 77.2090,
}


class StubClient:
    """A model that answers instantly and records what it was asked."""

    def __init__(self) -> None:
        self.requests: list[object] = []

    def complete(self, request):
        self.requests.append(request)
        return "Your Sun sits in the tenth house, so work is where you are seen."

    def stream(self, request):
        self.requests.append(request)
        yield "Your Sun sits in the tenth house."


@pytest.fixture
def stub():
    stubbed = StubClient()
    set_client(stubbed)
    yield stubbed
    set_client(None)


@pytest.fixture
def subscriber(monkeypatch):
    """A signed-in account that RevenueCat says is Pro."""
    monkeypatch.setattr(entitlements, "is_configured", lambda: True)
    monkeypatch.setattr(
        entitlements, "entitlement_of", lambda uid: entitlements.Entitlement(active=True)
    )
    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(
        id="user-1", email="reader@example.com"
    )
    yield
    app.dependency_overrides.clear()


@pytest.fixture
def freeloader(monkeypatch):
    """A signed-in account that has never bought anything."""
    monkeypatch.setattr(entitlements, "is_configured", lambda: True)
    monkeypatch.setattr(entitlements, "entitlement_of", lambda uid: entitlements.NOT_ENTITLED)
    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(id="user-2", email=None)
    yield
    app.dependency_overrides.clear()


# --- Reading an entitlement -------------------------------------------------


def _subscriber_body(expires: str | None) -> dict:
    return {
        "subscriber": {
            "entitlements": {
                "enuma_sky_pro": {
                    "expires_date": expires,
                    "product_identifier": "monthly",
                }
            }
        }
    }


def _answering(status: int, body: dict | None = None):
    def fake_get(url, **kwargs):
        return httpx.Response(
            status_code=status, json=body if body is not None else {}, request=httpx.Request("GET", url)
        )

    return fake_get


def test_a_lifetime_purchase_has_no_expiry_and_is_still_active(monkeypatch):
    """None means lifetime here and 'never bought' elsewhere. Only `active` decides."""
    monkeypatch.setattr(entitlements, "SECRET_KEY", "sk_test")
    monkeypatch.setattr(entitlements.httpx, "get", _answering(200, _subscriber_body(None)))
    entitlements._cache.clear()

    granted = entitlements.entitlement_of("user-lifetime")
    assert granted.active is True
    assert granted.expires_at is None


def test_an_entitlement_that_has_run_out_is_not_active(monkeypatch):
    """RevenueCat lists expired entitlements too, so the date is what decides."""
    monkeypatch.setattr(entitlements, "SECRET_KEY", "sk_test")
    past = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(days=1)).isoformat().replace(
        "+00:00", "Z"
    )
    monkeypatch.setattr(entitlements.httpx, "get", _answering(200, _subscriber_body(past)))
    entitlements._cache.clear()

    assert entitlements.entitlement_of("user-lapsed").active is False


def test_an_account_revenuecat_has_never_seen_is_simply_not_entitled(monkeypatch):
    """404 is an answer — somebody signed up and did not buy — not an error."""
    monkeypatch.setattr(entitlements, "SECRET_KEY", "sk_test")
    monkeypatch.setattr(entitlements.httpx, "get", _answering(404))
    entitlements._cache.clear()

    assert entitlements.entitlement_of("user-new").active is False


def test_an_unreachable_revenuecat_is_a_503_and_never_a_paywall(monkeypatch):
    """Being wrong here must not tell a paying subscriber they have not paid."""
    monkeypatch.setattr(entitlements, "SECRET_KEY", "sk_test")

    def unreachable(url, **kwargs):
        raise httpx.ConnectError("no route to host")

    monkeypatch.setattr(entitlements.httpx, "get", unreachable)
    entitlements._cache.clear()

    with pytest.raises(Exception) as raised:
        entitlements.entitlement_of("user-1")
    assert getattr(raised.value, "status_code", None) == 503


def test_a_rejected_secret_key_refuses_everyone_rather_than_letting_them_in(monkeypatch):
    """A configuration failure wearing a paywall's clothes. Closed, and logged."""
    monkeypatch.setattr(entitlements, "SECRET_KEY", "sk_wrong")
    monkeypatch.setattr(entitlements.httpx, "get", _answering(401))
    entitlements._cache.clear()

    with pytest.raises(Exception) as raised:
        entitlements.entitlement_of("user-1")
    assert getattr(raised.value, "status_code", None) == 503


# --- The gate ---------------------------------------------------------------


@pytest.mark.parametrize(
    "path,body",
    [
        ("/v1/interpret", {"birth": BIRTH}),
        ("/v1/tip", {"birth": BIRTH}),
        ("/v1/chat", {"birth": BIRTH, "question": "how is this year?"}),
        ("/v1/tarot/reading", {"seed": "abc123"}),
    ],
)
def test_every_endpoint_that_calls_a_model_is_behind_the_gate(path, body, stub, freeloader):
    """The whole point of the change, asserted once per endpoint.

    `/v1/interpret` and `/v1/tip` had no gate of any kind: no account, no
    charge, no limit, on a URL that ships inside the app binary. On a free model
    tier of twenty requests a day, that was a denial of service anyone could
    perform against the people who had paid.
    """
    response = client.post(path, json=body)
    assert response.status_code == 402, path
    assert stub.requests == [], f"{path} called the model before checking"


@pytest.mark.parametrize(
    "path,body",
    [
        ("/v1/interpret", {"birth": BIRTH}),
        ("/v1/tip", {"birth": BIRTH}),
        ("/v1/tarot/reading", {"seed": "abc123"}),
    ],
)
def test_a_subscriber_gets_through(path, body, stub, subscriber):
    assert client.post(path, json=body).status_code == 200


def test_signed_out_is_401_and_signed_in_without_a_plan_is_402(stub, monkeypatch):
    """Two different screens. One status for both would show the wrong one."""
    monkeypatch.setattr(entitlements, "is_configured", lambda: True)

    signed_out = client.post("/v1/interpret", json={"birth": BIRTH})
    assert signed_out.status_code == 401

    monkeypatch.setattr(entitlements, "entitlement_of", lambda uid: entitlements.NOT_ENTITLED)
    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(id="u", email=None)
    try:
        assert client.post("/v1/interpret", json={"birth": BIRTH}).status_code == 402
    finally:
        app.dependency_overrides.clear()


def test_the_deterministic_endpoints_stay_free(monkeypatch):
    """A chart is arithmetic. Nobody subscribes to arithmetic.

    This is the free tier now: everything the engine computes without a model
    is open, and every sentence a model writes is not.
    """
    monkeypatch.setattr(entitlements, "is_configured", lambda: True)

    assert client.post("/v1/chart", json=BIRTH).status_code == 200
    assert client.post("/v1/panchang", json=BIRTH).status_code == 200
    assert client.post("/v1/dasha", json=BIRTH).status_code == 200
    assert client.post("/v1/reading", json=BIRTH).status_code == 200
    assert client.post("/v1/today", json=BIRTH).status_code == 200
    assert client.get("/v1/places", params={"q": "Delhi"}).status_code == 200
    assert client.get("/v1/course", params={"language": "en"}).status_code == 200


def test_a_client_cannot_replay_its_way_past_the_gate(stub, freeloader):
    """The regression for the bug that made the old paywall optional.

    The ledger it replaced took a credit against a `request_id` the client
    chose, and answered a repeat with "already paid, carry on". So the same id
    sent forever was charged exactly once, ever, and a modified app got
    unlimited paid messages for the price of one.

    There is no key to repeat now — `request_id` is not in the schema and the
    gate holds no per-request state — so a hundred identical requests are a
    hundred refusals rather than one refusal and ninety-nine free answers.
    """
    for _ in range(5):
        sent = client.post(
            "/v1/tarot/reading", json={"seed": "abc123", "request_id": "always-the-same"}
        )
        assert sent.status_code == 402

    assert stub.requests == []


def test_an_unconfigured_deployment_gates_nothing(stub, monkeypatch):
    """The engine has to run locally without anyone standing up billing."""
    monkeypatch.setattr(entitlements, "is_configured", lambda: False)
    assert client.post("/v1/interpret", json={"birth": BIRTH}).status_code == 200


# --- The ceiling ------------------------------------------------------------


@pytest.fixture(autouse=True)
def _fresh_limits():
    ratelimit.reset_all()
    yield
    ratelimit.reset_all()


def test_a_subscriber_is_unlimited_the_way_a_person_means_it(stub, subscriber, monkeypatch):
    """Not the way a script means it. Twenty a minute is far above a conversation."""
    monkeypatch.setattr(ratelimit.AI, "limit", 3)

    for _ in range(3):
        assert client.post("/v1/tarot/reading", json={"seed": "abc123"}).status_code == 200

    stopped = client.post("/v1/tarot/reading", json={"seed": "abc123"})
    assert stopped.status_code == 429
    assert "Retry-After" in stopped.headers


def test_the_limit_is_keyed_on_the_account_not_the_address(stub, monkeypatch):
    """One office network is many phones, and one of them must not throttle the rest."""
    monkeypatch.setattr(entitlements, "is_configured", lambda: True)
    monkeypatch.setattr(
        entitlements, "entitlement_of", lambda uid: entitlements.Entitlement(active=True)
    )
    monkeypatch.setattr(ratelimit.AI, "limit", 1)

    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(id="first", email=None)
    try:
        assert client.post("/v1/tarot/reading", json={"seed": "abc123"}).status_code == 200
        assert client.post("/v1/tarot/reading", json={"seed": "abc123"}).status_code == 429
    finally:
        app.dependency_overrides.clear()

    app.dependency_overrides[auth.optional_user] = lambda: auth.Account(id="second", email=None)
    try:
        # A different account, still inside the first one's window.
        assert client.post("/v1/tarot/reading", json={"seed": "abc123"}).status_code == 200
    finally:
        app.dependency_overrides.clear()


def test_everything_has_a_ceiling_including_the_free_endpoints(monkeypatch):
    """`/v1/places` scans three thousand rows on every keystroke."""
    monkeypatch.setattr(ratelimit.GLOBAL, "limit", 2)

    assert client.get("/v1/places", params={"q": "Delhi"}).status_code == 200
    assert client.get("/v1/places", params={"q": "Delhi"}).status_code == 200

    stopped = client.get("/v1/places", params={"q": "Delhi"})
    assert stopped.status_code == 429
    assert stopped.headers["Retry-After"]


# --- What the server no longer tells strangers ------------------------------


def test_health_no_longer_says_whether_the_paywall_is_on():
    """It used to answer that, unauthenticated, before anyone tried the paywall."""
    body = client.get("/health").json()
    assert body["status"] == "ok"
    assert "billing" not in body
    assert "cache" not in body


def test_the_cache_stats_need_the_operator_token():
    assert client.get("/v1/health/cache").status_code == 404
    assert client.get("/v1/health/cache", params={"token": "guess"}).status_code == 404

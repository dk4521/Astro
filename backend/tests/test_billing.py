"""Tests for the paid path.

Nothing here talks to Razorpay or Supabase. What is worth testing is not that
those services work — it is the seam either side of them: that a forged webhook
is refused, that a real one grants exactly what was bought, and that a message
cannot be generated without a credit having been taken first.

The four failures these are written against, all of which are easy to ship and
none of which are visible by reading the happy path:

  a webhook accepted without a signature, which is a free-credits API
  a webhook delivered twice granting twice, which Razorpay guarantees will happen
  a checkout that trusts an amount from the device
  a credit taken for an answer the model never produced
"""

from __future__ import annotations

import hashlib
import hmac
import json

import pytest
from fastapi.testclient import TestClient

from app import auth
from app.api import billing as billing_routes
from app.api import routes as api_routes
from app.billing import gateway, plans, store
from app.main import app

client = TestClient(app)


# --- The catalogue ----------------------------------------------------------


def test_plans_are_hidden_when_nothing_can_be_charged():
    """A price nobody can pay is worse than no price at all."""
    response = client.get("/v1/billing/plans")
    assert response.status_code == 200
    body = response.json()
    if not body["enabled"]:
        assert body["plans"] == []


def test_pack_and_subscription_pricing_stay_far_apart():
    """The gap is the product's advice, so it is worth asserting.

    A pack costs roughly ten times a subscription message. If a price edit ever
    closes that gap, packs quietly become the rational choice for heavy users
    and the subscription stops being worth selling.
    """
    pack = plans.get("pack_m")
    monthly = plans.get("monthly")
    assert pack and monthly

    per_pack_message = pack.amount_paise / pack.credits
    per_sub_message = monthly.amount_paise / monthly.credits
    assert per_pack_message > per_sub_message * 5


def test_subscriptions_without_a_razorpay_plan_id_are_not_offered(monkeypatch):
    """Configuration missing must mean "not for sale", never "sold and then broken"."""
    monkeypatch.delenv("RAZORPAY_PLAN_MONTHLY", raising=False)
    monkeypatch.delenv("RAZORPAY_PLAN_YEARLY", raising=False)

    offered = {p.id for p in plans.offered()}
    assert "pack_m" in offered
    assert "monthly" not in offered and "yearly" not in offered


# --- Webhook signatures -----------------------------------------------------


def _sign(body: bytes, secret: str) -> str:
    return hmac.new(secret.encode(), body, hashlib.sha256).hexdigest()


def test_signature_must_match_the_exact_bytes(monkeypatch):
    monkeypatch.setattr(gateway, "WEBHOOK_SECRET", "shhh")
    body = b'{"event":"payment_link.paid"}'

    assert gateway.verify_webhook(body, _sign(body, "shhh"))
    assert not gateway.verify_webhook(body + b" ", _sign(body, "shhh"))
    assert not gateway.verify_webhook(body, _sign(body, "wrong-secret"))
    assert not gateway.verify_webhook(body, None)


def test_no_configured_secret_rejects_everything(monkeypatch):
    """A deployment that forgot the secret must reject, not wave things through."""
    monkeypatch.setattr(gateway, "WEBHOOK_SECRET", "")
    body = b'{"event":"payment_link.paid"}'
    assert not gateway.verify_webhook(body, _sign(body, ""))


def test_unsigned_webhook_is_refused():
    response = client.post("/v1/billing/webhook", json={"event": "payment_link.paid"})
    assert response.status_code == 400


# --- What a webhook grants --------------------------------------------------


class FakeStore:
    """Records what would have been written, and can be told to fail."""

    def __init__(self, *, fail: bool = False):
        self.grants: list[tuple] = []
        self.payments: list[tuple] = []
        self.subscriptions: list[tuple] = []
        self.ensured: list[str] = []
        self.fail = fail
        self.seen_refs: set[str] = set()

    def grant_credits(self, user_id, credits, source, source_ref, expires_at=None):
        if self.fail:
            raise store.StoreError("supabase is down")
        # Mirrors the unique index on (user_id, source_ref): a repeat grants
        # nothing and returns no lot.
        if source_ref in self.seen_refs:
            return None
        self.seen_refs.add(source_ref)
        self.grants.append((user_id, credits, source, source_ref, expires_at))
        return "lot-1"

    def record_payment(self, user_id, payment_id, order_id, product, amount_paise, status):
        if self.fail:
            raise store.StoreError("supabase is down")
        self.payments.append((user_id, payment_id, product, amount_paise, status))

    def record_subscription(self, user_id, plan, status, provider_id, period_end=None):
        if self.fail:
            raise store.StoreError("supabase is down")
        self.subscriptions.append((user_id, plan, status, provider_id, period_end))

    def ensure_grants(self, user_id):
        self.ensured.append(user_id)


@pytest.fixture
def signed(monkeypatch):
    """A client that can post webhooks, against a store that only remembers."""
    fake = FakeStore()
    monkeypatch.setattr(gateway, "verify_webhook", lambda body, sig: True)
    for name in ("grant_credits", "record_payment", "record_subscription", "ensure_grants"):
        monkeypatch.setattr(billing_routes.store, name, getattr(fake, name))
    return fake


def _pack_event(payment_id: str = "pay_1", plan_id: str = "pack_m") -> dict:
    return {
        "event": "payment_link.paid",
        "payload": {
            "payment_link": {
                "entity": {"id": "plink_1", "notes": {"user_id": "user-1", "plan_id": plan_id}}
            },
            "payment": {"entity": {"id": payment_id, "status": "captured", "order_id": "order_1"}},
        },
    }


def test_a_pack_grants_the_credits_the_catalogue_says(signed):
    response = client.post("/v1/billing/webhook", json=_pack_event())
    assert response.status_code == 200

    user_id, credits, source, source_ref, expires_at = signed.grants[0]
    assert user_id == "user-1"
    assert credits == plans.get("pack_m").credits
    assert source == "pack"
    # Keyed on the payment, which is what makes the second delivery free.
    assert source_ref == "pay:pay_1"
    assert expires_at is not None


def test_the_amount_recorded_comes_from_the_catalogue_not_the_event(signed):
    """The webhook body is attacker-shaped input the moment a signature leaks.

    Reading the price from `plans.py` rather than from the payload means a
    forged amount cannot decide how many credits appear.
    """
    event = _pack_event()
    event["payload"]["payment"]["entity"]["amount"] = 100  # one rupee, claimed
    client.post("/v1/billing/webhook", json=event)

    _, _, _, amount, _ = signed.payments[0]
    assert amount == plans.get("pack_m").amount_paise


def test_the_same_payment_delivered_twice_grants_once(signed):
    first = client.post("/v1/billing/webhook", json=_pack_event())
    second = client.post("/v1/billing/webhook", json=_pack_event())

    assert first.status_code == second.status_code == 200
    assert len(signed.grants) == 1
    assert second.json()["outcome"] == "already granted"


def test_an_event_with_no_notes_is_dropped_rather_than_guessed_at(signed):
    event = _pack_event()
    event["payload"]["payment_link"]["entity"]["notes"] = {}

    response = client.post("/v1/billing/webhook", json=event)
    assert response.status_code == 200
    assert signed.grants == []


def test_an_unknown_plan_id_grants_nothing(signed):
    response = client.post("/v1/billing/webhook", json=_pack_event(plan_id="pack_free_lol"))
    assert response.status_code == 200
    assert signed.grants == []


def test_an_unhandled_event_is_answered_200_so_razorpay_stops_retrying(signed):
    response = client.post(
        "/v1/billing/webhook", json={"event": "payment.failed", "payload": {}}
    )
    assert response.status_code == 200
    assert response.json()["status"] == "ignored"


def test_a_database_failure_asks_razorpay_to_retry(monkeypatch):
    """500, not 200. A paid-for credit must survive Supabase being briefly down."""
    fake = FakeStore(fail=True)
    monkeypatch.setattr(gateway, "verify_webhook", lambda body, sig: True)
    for name in ("grant_credits", "record_payment", "record_subscription"):
        monkeypatch.setattr(billing_routes.store, name, getattr(fake, name))

    response = client.post("/v1/billing/webhook", json=_pack_event())
    assert response.status_code == 500


def test_an_active_subscription_records_and_grants(signed):
    event = {
        "event": "subscription.charged",
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_1",
                    "status": "active",
                    "current_end": 1_800_000_000,
                    "notes": {"user_id": "user-1", "plan_id": "yearly"},
                }
            },
            "payment": {"entity": {"id": "pay_2", "status": "captured", "amount": 79900}},
        },
    }
    response = client.post("/v1/billing/webhook", json=event)
    assert response.status_code == 200

    user_id, plan, status, provider_id, period_end = signed.subscriptions[0]
    assert (user_id, plan, status, provider_id) == ("user-1", "yearly", "active", "sub_1")
    assert period_end is not None and period_end.startswith("2027-")
    # Credits appear without waiting for the app to ask for them.
    assert signed.ensured == ["user-1"]


def test_a_halted_subscription_records_but_grants_nothing(signed):
    """A failed mandate keeps what was already given and adds no month."""
    event = {
        "event": "subscription.halted",
        "payload": {
            "subscription": {
                "entity": {
                    "id": "sub_1",
                    "status": "halted",
                    "notes": {"user_id": "user-1", "plan_id": "monthly"},
                }
            }
        },
    }
    client.post("/v1/billing/webhook", json=event)

    assert signed.subscriptions[0][2] == "halted"
    assert signed.ensured == []


# --- The gate on a message --------------------------------------------------


def test_billing_off_leaves_chat_open(monkeypatch):
    """The engine has to remain runnable with no Supabase project at all."""
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: False)
    charged_to, ref, balance = api_routes._charge(None, None)
    assert charged_to is None


def test_billing_on_without_a_session_is_401(monkeypatch):
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: True)
    with pytest.raises(api_routes.HTTPException) as raised:
        api_routes._charge(None, None)
    assert raised.value.status_code == 401


def test_out_of_credits_is_402_not_401(monkeypatch):
    """Two different problems, two different screens.

    401 sends someone to sign in, which they have already done. Collapsing
    these is the kind of bug that reads fine and strands a paying user.
    """
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: True)
    monkeypatch.setattr(api_routes.store, "consume_credit", lambda uid, ref: (False, 0))

    with pytest.raises(api_routes.HTTPException) as raised:
        api_routes._charge(auth.Account(id="user-1", email=None), "req-1")
    assert raised.value.status_code == 402


def test_a_credit_is_taken_before_any_token_is_generated(monkeypatch):
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: True)
    seen: list[tuple[str, str]] = []

    def consume(user_id, ref):
        seen.append((user_id, ref))
        return True, 41

    monkeypatch.setattr(api_routes.store, "consume_credit", consume)

    charged_to, ref, balance = api_routes._charge(
        auth.Account(id="user-1", email=None), "req-7"
    )
    assert (charged_to, ref, balance) == ("user-1", "req-7", 41)
    assert seen == [("user-1", "req-7")]


def test_supabase_being_unreachable_closes_the_door(monkeypatch):
    """Falling open here would make the paywall optional for anyone who can time it out."""
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: True)

    def boom(user_id, ref):
        raise store.StoreError("timeout")

    monkeypatch.setattr(api_routes.store, "consume_credit", boom)

    with pytest.raises(api_routes.HTTPException) as raised:
        api_routes._charge(auth.Account(id="user-1", email=None), "req-1")
    assert raised.value.status_code == 503


def test_a_missing_request_id_still_charges_exactly_once(monkeypatch):
    """No idempotency key means no replay protection, never a free message."""
    monkeypatch.setattr(api_routes.store, "is_configured", lambda: True)
    calls: list[str] = []
    monkeypatch.setattr(
        api_routes.store, "consume_credit",
        lambda uid, ref: (calls.append(ref), (True, 5))[1],
    )

    _, first, _ = api_routes._charge(auth.Account(id="u", email=None), None)
    _, second, _ = api_routes._charge(auth.Account(id="u", email=None), None)

    assert len(calls) == 2
    assert first != second and first and second


# --- Sessions ---------------------------------------------------------------


def test_a_bearerless_header_is_nobody():
    assert auth._bearer(None) is None
    assert auth._bearer("") is None
    assert auth._bearer("Basic abc") is None
    assert auth._bearer("Bearer ") is None
    assert auth._bearer("Bearer abc.def.ghi") == "abc.def.ghi"


def test_tokens_are_never_used_as_cache_keys_in_the_clear(monkeypatch):
    """A token is a credential; a heap dump should not be a list of them."""
    monkeypatch.setattr(auth, "SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setattr(auth, "_API_KEY", "anon")

    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {"id": "user-1", "email": "a@b.c"}

    monkeypatch.setattr(auth.httpx, "get", lambda *a, **k: Response())
    auth._cache.clear()

    account = auth._verify("secret-token")
    assert account == auth.Account(id="user-1", email="a@b.c")
    assert "secret-token" not in json.dumps(list(auth._cache.keys()))
    auth._cache.clear()

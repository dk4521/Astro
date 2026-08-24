"""Billing endpoints.

Four things happen here: the app asks what is for sale, the app asks for a
checkout page, Razorpay reports that money moved, and someone cancels.

Reading a balance is deliberately not one of them. The app already holds a
Supabase session, and `credit_summary()` is the one function in the schema
granted to `authenticated` — so the balance comes straight from Postgres over
a connection that already exists, rather than through a backend that would only
be forwarding it.
"""

from __future__ import annotations

import datetime as dt
import json
import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from pydantic import BaseModel, Field

from .. import auth
from ..billing import gateway, plans, store

log = logging.getLogger("kosmiq.billing")

router = APIRouter(prefix="/billing", tags=["billing"])


# --- What is for sale -------------------------------------------------------


class PlanOut(BaseModel):
    id: str
    kind: str
    label: str
    amount_paise: int
    rupees: int
    credits: int
    period: str | None = None
    validity_days: int | None = None


class PlansResponse(BaseModel):
    #: False on a deployment with no Razorpay keys. The app hides the pricing
    #: screen rather than showing plans that cannot be bought.
    enabled: bool
    currency: str = "INR"
    plans: list[PlanOut]


@router.get("/plans", response_model=PlansResponse, summary="What credits cost")
def catalogue() -> PlansResponse:
    """Prices come from the server so that changing one is not an app release.

    A store build from six months ago still draws today's prices, and — more
    to the point — cannot draw a price this server would refuse to charge.
    """
    available = gateway.is_configured() and store.is_configured()
    return PlansResponse(
        enabled=available,
        plans=[
            PlanOut(
                id=p.id, kind=p.kind, label=p.label, amount_paise=p.amount_paise,
                rupees=p.rupees, credits=p.credits, period=p.period,
                validity_days=p.validity_days,
            )
            for p in (plans.offered() if available else [])
        ],
    )


# --- Checkout ---------------------------------------------------------------


class CheckoutRequest(BaseModel):
    plan_id: str = Field(..., max_length=64)


class CheckoutResponse(BaseModel):
    #: Razorpay's hosted page. The app opens it in a browser and waits to be
    #: returned to its deep link.
    url: str
    reference: str
    kind: str


@router.post("/checkout", response_model=CheckoutResponse, summary="Begin a purchase")
def checkout(
    payload: CheckoutRequest,
    account: auth.Account = Depends(auth.require_user),
) -> CheckoutResponse:
    """Turn a plan id into a page to pay on.

    The request carries a plan id and nothing else — no amount, no credit
    count, no user id. All three are decided here, from `plans.py` and from the
    verified session, because every one of them is a number a client would
    otherwise be able to choose for itself.
    """
    if not (gateway.is_configured() and store.is_configured()):
        raise HTTPException(status_code=503, detail="Payments are not available yet.")

    plan = plans.get(payload.plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="No such plan.")

    try:
        if plan.kind == "subscription":
            created = gateway.create_subscription(plan, account.id, account.email)
        else:
            created = gateway.create_pack_link(plan, account.id, account.email)
    except gateway.GatewayError as exc:
        log.warning("checkout failed for %s (%s): %s", account.id, plan.id, exc)
        raise HTTPException(
            status_code=502, detail="Could not open checkout. Try again in a moment."
        ) from exc

    return CheckoutResponse(url=created["url"], reference=created["id"], kind=plan.kind)


# --- Cancelling -------------------------------------------------------------


class CancelRequest(BaseModel):
    subscription_id: str = Field(..., max_length=128)


@router.post("/cancel", summary="Stop a subscription at the end of the period")
def cancel(account: auth.Account = Depends(auth.require_user)) -> dict[str, str]:
    """Cancel, but not before what has been paid for runs out.

    The subscription is looked up from the session rather than named by the
    request. An endpoint that cancelled whatever id it was handed would cancel
    other people's subscriptions for anyone willing to guess, and there is no
    reason for the client to know the id at all.
    """
    if not (gateway.is_configured() and store.is_configured()):
        raise HTTPException(status_code=503, detail="Payments are not available yet.")

    subscription = store.live_subscription(account.id)
    if not subscription:
        raise HTTPException(status_code=404, detail="There is no subscription to cancel.")

    try:
        gateway.cancel_subscription(str(subscription["provider_id"]), at_period_end=True)
    except gateway.GatewayError as exc:
        log.warning("cancel failed for %s: %s", account.id, exc)
        raise HTTPException(
            status_code=502, detail="Could not cancel just now. Try again in a moment."
        ) from exc

    # Razorpay will also say so by webhook; writing it here means the app sees
    # the change on its next refresh instead of whenever the webhook lands.
    store.record_subscription(
        account.id,
        plan=str(subscription["plan"]),
        status="cancelled",
        provider_id=str(subscription["provider_id"]),
        period_end=subscription.get("current_period_end"),
    )

    return {
        "status": "cancelled",
        "detail": "Your plan stays active until the end of the period you have paid for.",
    }


# --- The webhook ------------------------------------------------------------
#
# This is where credits actually come from. Not the checkout call, which only
# opens a page, and not the browser returning to the app, which may never
# happen. Razorpay signs this request and retries it until it is answered with
# a 2xx, which is the only delivery guarantee in the whole flow.
#
# Everything here is idempotent, because "retries until answered" means the
# same event will arrive twice sooner or later. Both keys are unique indexes in
# the schema: a pack grants against `pay:<payment_id>`, a subscription month
# against `sub:<id>:<month>`. A second delivery inserts nothing and reports
# success, which is the truth — those credits do exist.


def _iso(unix_seconds: object) -> str | None:
    """Razorpay's epoch timestamps as something Postgres will accept."""
    if not isinstance(unix_seconds, (int, float)):
        return None
    return dt.datetime.fromtimestamp(float(unix_seconds), tz=dt.timezone.utc).isoformat()


def _entity(payload: dict, name: str) -> dict:
    section = payload.get(name)
    if isinstance(section, dict):
        entity = section.get("entity")
        if isinstance(entity, dict):
            return entity
    return {}


def _notes(entity: dict) -> tuple[str | None, str | None]:
    """The account and plan a checkout was opened for.

    Carried in Razorpay's `notes`, which is the only field that makes the round
    trip from checkout to webhook. An event without them is not something to
    guess at — there is no safe way to decide whose credits these are — so the
    caller drops it.
    """
    notes = entity.get("notes")
    if not isinstance(notes, dict):
        return None, None
    user_id = notes.get("user_id")
    plan_id = notes.get("plan_id")
    return (
        user_id if isinstance(user_id, str) and user_id else None,
        plan_id if isinstance(plan_id, str) and plan_id else None,
    )


def _on_pack_paid(payload: dict) -> str:
    link = _entity(payload, "payment_link")
    payment = _entity(payload, "payment")

    user_id, plan_id = _notes(link)
    payment_id = payment.get("id")
    if not (user_id and plan_id and isinstance(payment_id, str)):
        return "ignored: incomplete payment_link event"

    plan = plans.get(plan_id)
    if plan is None or plan.kind != "pack":
        return f"ignored: unknown pack {plan_id}"

    store.record_payment(
        user_id,
        payment_id=payment_id,
        order_id=payment.get("order_id") if isinstance(payment.get("order_id"), str) else None,
        product=plan.id,
        amount_paise=plan.amount_paise,
        status=str(payment.get("status") or "captured"),
    )

    expires_at = None
    if plan.validity_days:
        expires_at = (
            dt.datetime.now(dt.timezone.utc) + dt.timedelta(days=plan.validity_days)
        ).isoformat()

    lot = store.grant_credits(
        user_id, plan.credits, source="pack",
        source_ref=f"pay:{payment_id}", expires_at=expires_at,
    )
    return "granted" if lot else "already granted"


def _on_subscription(event: str, payload: dict) -> str:
    entity = _entity(payload, "subscription")
    user_id, plan_id = _notes(entity)
    provider_id = entity.get("id")

    if not (user_id and plan_id and isinstance(provider_id, str)):
        return "ignored: incomplete subscription event"

    plan = plans.get(plan_id)
    if plan is None or plan.kind != "subscription":
        return f"ignored: unknown subscription plan {plan_id}"

    # `cancelled` arriving for a subscription cancelled at cycle end still
    # means "no more charges", not "stop now" — the credits already granted
    # keep their own expiry, which is the end of the period that paid for them.
    status = str(entity.get("status") or event.split(".")[-1])

    store.record_subscription(
        user_id, plan=plan.id, status=status,
        provider_id=provider_id, period_end=_iso(entity.get("current_end")),
    )

    if event == "subscription.charged":
        payment = _entity(payload, "payment")
        payment_id = payment.get("id")
        if isinstance(payment_id, str):
            store.record_payment(
                user_id, payment_id=payment_id,
                order_id=payment.get("order_id") if isinstance(payment.get("order_id"), str) else None,
                product=plan.id,
                amount_paise=int(payment.get("amount") or plan.amount_paise),
                status=str(payment.get("status") or "captured"),
            )

    if status == "active":
        # The lazy grant in the schema would do this on the next balance read.
        # Doing it now is what makes the credits already be there when someone
        # closes the payment page and looks at the app.
        store.ensure_grants(user_id)

    return f"recorded {status}"


HANDLED = {
    "payment_link.paid",
    "subscription.activated",
    "subscription.charged",
    "subscription.pending",
    "subscription.halted",
    "subscription.cancelled",
    "subscription.completed",
}


@router.post("/webhook", summary="Razorpay tells us money moved")
async def webhook(request: Request) -> dict[str, str]:
    """Signed, replay-safe, and the only path that creates paid credits.

    The body is read as bytes and parsed here rather than declared as a Pydantic
    model, because the signature covers the exact bytes Razorpay sent. Letting
    FastAPI parse and re-serialise would compare a signature against a
    different string and reject every genuine call.
    """
    body = await request.body()

    if not gateway.verify_webhook(body, request.headers.get("X-Razorpay-Signature")):
        # 400, not 401: there is no session to be missing, and the answer must
        # not tell an attacker which part of the guess was wrong.
        raise HTTPException(status_code=400, detail="Invalid signature.")

    try:
        event_body = json.loads(body)
    except ValueError:
        raise HTTPException(status_code=400, detail="Malformed body.") from None

    event = str(event_body.get("event") or "")
    payload = event_body.get("payload")
    if not isinstance(payload, dict) or event not in HANDLED:
        # A 200 on purpose. Razorpay retries anything else, and retrying an
        # event this build does not handle would go on until it gave up.
        return {"status": "ignored", "event": event}

    try:
        if event == "payment_link.paid":
            outcome = _on_pack_paid(payload)
        else:
            outcome = _on_subscription(event, payload)
    except store.StoreError as exc:
        # 500 so Razorpay retries. Supabase being briefly unreachable must not
        # cost someone the credits they paid for.
        log.error("webhook %s failed: %s", event, exc)
        raise HTTPException(status_code=500, detail="Could not record the payment.") from exc

    log.info("webhook %s: %s", event, outcome)
    return {"status": "ok", "event": event, "outcome": outcome}

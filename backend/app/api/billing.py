"""What the server believes about a subscription.

Almost nothing lives here any more, and that is the point of the change. This
file used to run a payment gateway: a catalogue, a checkout call, a cancel
call, and a signed webhook that was the only path by which credits could come
into existence. All four are gone with Razorpay, because the store now sells
the subscription and RevenueCat holds the record of it.

What is left is one endpoint that answers "does the server agree that I am
Pro". Nothing in the app *needs* it — `usePurchases()` already knows, from the
same SDK that made the purchase — and that is exactly why it is worth having.
The two answers can disagree in ways worth seeing: a purchase that succeeded on
the device but never reached RevenueCat, a `logIn` that never attached the
purchase to the account, a secret key that expired on this side. Without this,
each of those looks to the reader like "the app took my money and shows me a
paywall", and looks to us like nothing at all.

Prices are not here either. They come from the store, already localised, already
carrying whatever introductory offer this particular buyer qualifies for. A
price in this file would be a fourth copy of a number that App Store Connect,
Play Console and RevenueCat already hold — and the only one of the four that
could be wrong without anyone noticing.
"""

from __future__ import annotations

import datetime as dt

from fastapi import APIRouter, Depends
from pydantic import BaseModel

from .. import auth, entitlements, ratelimit

router = APIRouter(prefix="/billing", tags=["billing"])


class StatusResponse(BaseModel):
    #: False on a deployment with no RevenueCat secret key, where nothing is
    #: for sale and nothing is gated. The app hides the upgrade path.
    enabled: bool
    signed_in: bool
    pro: bool
    #: None for a lifetime purchase *and* for no purchase. Read `pro` first.
    expires_at: dt.datetime | None = None
    product: str | None = None


@router.get("/status", response_model=StatusResponse, summary="Is this account Pro")
def status(account: auth.Account | None = Depends(auth.optional_user)) -> StatusResponse:
    """Deliberately not gated, and deliberately not an error when signed out.

    A paywall screen asks this, and a paywall screen is the one place someone
    who is *not* entitled has every right to be. Refusing them with a 402 here
    would mean the screen selling the subscription could not draw itself.
    """
    if not entitlements.is_configured():
        return StatusResponse(enabled=False, signed_in=account is not None, pro=False)

    if account is None:
        return StatusResponse(enabled=True, signed_in=False, pro=False)

    granted = entitlements.entitlement_of(account.id)
    return StatusResponse(
        enabled=True,
        signed_in=True,
        pro=granted.active,
        expires_at=granted.expires_at,
        product=granted.product,
    )


@router.post("/refresh", response_model=StatusResponse, summary="Re-read after a purchase")
def refresh(account: auth.Account = Depends(auth.require_user)) -> StatusResponse:
    """The same answer, with the cache dropped first.

    Entitlements are cached for a minute, which is right for every read except
    the one immediately after paying — where a stale "not subscribed" is the
    worst sentence this product can show a person who has just been charged. The
    app calls this once when a purchase completes and then trusts the cache
    again.

    Limited, because dropping a cache entry on demand is a way to make this
    server call RevenueCat as often as someone likes. A purchase happens once;
    thirty of these a minute is not one.
    """
    ratelimit.AUTH.check(f"refresh:{account.id}")
    entitlements.forget(account.id)
    return status(account)

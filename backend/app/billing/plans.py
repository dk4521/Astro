"""What is for sale, in one place.

Prices live here rather than in the app, the database or the Razorpay
dashboard, because the app has to draw them, the database has to grant against
them and Razorpay has to charge them — and three copies of a price is two
chances to sell something for the wrong amount. The client fetches this
catalogue from `/v1/billing/plans` and renders whatever it is given.

**The shape.** One currency: a message costs one credit. Packs buy credits
outright; subscriptions rent them by the month. The two are priced far apart on
purpose — a pack is around eighty paise a message, a subscription around seven.
That gap is the product telling the truth about itself: someone who asks three
questions a month should not be paying ninety-nine rupees for it, and someone
who asks three a day should not be buying packs.

**One number is duplicated and cannot be helped.** `MONTHLY_CREDITS` is also
written into `ensure_subscription_grant()` in supabase/schema.sql, because that
is where the granting happens and a Postgres function cannot read this file.
The comment there says the same thing in the other direction.
"""

from __future__ import annotations

import os
from dataclasses import dataclass

#: Credits a subscription grants each calendar month. Mirrored in the schema.
MONTHLY_CREDITS = 1500


@dataclass(frozen=True)
class Plan:
    """One purchasable thing."""

    id: str
    kind: str  # "pack" or "subscription"
    label: str
    amount_paise: int
    #: A pack grants this once. A subscription grants it every month.
    credits: int
    #: How long bought credits last. None for subscriptions, whose credits
    #: expire with the period that granted them.
    validity_days: int | None = None
    period: str | None = None  # "monthly" or "yearly"

    @property
    def rupees(self) -> int:
        return self.amount_paise // 100


# Packs are ordered smallest first because that is how the screen reads, and
# the smallest one exists to be bought on impulse rather than to be economical.
PACKS: tuple[Plan, ...] = (
    Plan("pack_s", "pack", "20 messages", 1_900, credits=20, validity_days=365),
    Plan("pack_m", "pack", "60 messages", 4_900, credits=60, validity_days=365),
    Plan("pack_l", "pack", "200 messages", 14_900, credits=200, validity_days=365),
)

SUBSCRIPTIONS: tuple[Plan, ...] = (
    Plan(
        "monthly", "subscription", "Monthly",
        9_900, credits=MONTHLY_CREDITS, period="monthly",
    ),
    # A third off, not the sixteen percent that ₹999 would have been. Below
    # about a quarter off, an annual plan in this market is decoration: people
    # read it, do the division, and stay on monthly.
    Plan(
        "yearly", "subscription", "Yearly",
        79_900, credits=MONTHLY_CREDITS, period="yearly",
    ),
)

ALL: dict[str, Plan] = {p.id: p for p in (*PACKS, *SUBSCRIPTIONS)}


def get(plan_id: str) -> Plan | None:
    return ALL.get(plan_id)


def razorpay_plan_id(plan: Plan) -> str | None:
    """The Razorpay Plan this subscription maps to.

    Razorpay subscriptions are charged against a Plan object created in its
    dashboard, and that object's id is not derivable from anything here — so it
    is configuration, and a subscription whose id is missing is simply not
    offered rather than offered and then failing at checkout.
    """
    if plan.kind != "subscription":
        return None
    return os.environ.get(f"RAZORPAY_PLAN_{plan.id.upper()}", "").strip() or None


def offered() -> list[Plan]:
    """The catalogue as this deployment can actually sell it."""
    return [*PACKS, *(p for p in SUBSCRIPTIONS if razorpay_plan_id(p))]

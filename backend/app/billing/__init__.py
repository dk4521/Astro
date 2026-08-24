"""Charging for messages.

Three files, three jobs:

  `plans.py`    what is for sale, and the only place a price is written
  `gateway.py`  Razorpay — opening a checkout page, and proving a webhook is real
  `store.py`    Supabase with the service-role key — granting and spending credits

The rule that holds them apart: `gateway` never touches the database and
`store` never talks to Razorpay. What joins them is `app/api/billing.py`, which
is also the only place that has seen a verified session.
"""

from . import gateway, plans, store

__all__ = ["gateway", "plans", "store"]

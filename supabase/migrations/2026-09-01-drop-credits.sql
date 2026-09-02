-- Remove the credit ledger.
--
-- Run this once, in the SQL editor, on a project that ran the old schema.sql.
-- A project created from the current schema.sql has none of these objects and
-- does not need it.
--
--   ⚠ THIS DESTROYS THE PAYMENT HISTORY. `payments` and `subscriptions` are
--   the only record this project holds of what anyone was charged through
--   Razorpay. Export them first if there is any chance of a refund, a dispute
--   or a tax question about a purchase made before today:
--
--     select * from public.payments      order by created_at;
--     select * from public.subscriptions order by created_at;
--
--   Save both as CSV from the SQL editor's download button before running
--   anything below. Nothing here can be undone.
--
-- **Why any of this is going.** The ledger metered messages against an
-- idempotency key that the client chose, and answered a repeated key with
-- "already paid". So one fixed `request_id`, sent forever, was charged exactly
-- once — a modified app had unlimited paid messages for the price of the
-- smallest pack. The replacement is not a better key: a subscription is not a
-- currency, so there is nothing to meter and nothing to replay. RevenueCat
-- holds the record of who has access, and the backend asks it.
--
-- **What people lose.** Unspent credits. Anyone holding a pack bought them
-- outright, so decide what to do about that before running this — a free month
-- of Pro, granted in the RevenueCat dashboard, is the usual answer and the one
-- this project can actually deliver. The query below is who they are:
--
--   select user_id, sum(remaining) as credits_left
--   from public.credit_lots
--   where remaining > 0
--     and source = 'pack'
--     and (expires_at is null or expires_at > now())
--   group by user_id
--   order by credits_left desc;

begin;

-- --- Functions --------------------------------------------------------------
-- Dropped before the tables, so nothing is left pointing at a table that has
-- gone. `if exists` throughout, because this file has to be safe to run on a
-- project that has already had half of it applied.

drop function if exists public.credit_summary();
drop function if exists public.credit_balance_of(uuid);
drop function if exists public.ensure_free_grant(uuid);
drop function if exists public.ensure_subscription_grant(uuid);
drop function if exists public.ensure_grants(uuid);
drop function if exists public.grant_credits(uuid, integer, text, text, timestamptz);
drop function if exists public.consume_credit(uuid, text);
drop function if exists public.refund_credit(uuid, text);
drop function if exists public.record_subscription(uuid, text, text, text, timestamptz);
drop function if exists public.record_payment(uuid, text, text, text, integer, text);

-- --- Tables -----------------------------------------------------------------
-- `credit_spends` references `credit_lots`, so it goes first. The policies and
-- indexes on each go with the table; there is nothing to drop separately.

drop table if exists public.credit_spends;
drop table if exists public.credit_lots;
drop table if exists public.payments;
drop table if exists public.subscriptions;

-- --- The plan column --------------------------------------------------------
-- A cache of what `subscriptions` said, and now a cache of nothing. The
-- service-role policy that maintained it goes with it — no role writes profiles
-- any more except its owner, through the policy in schema.sql.

drop policy if exists "service writes profiles" on public.profiles;

-- The client's update policy has to go *before* the column, not after it. Its
-- `with check` reads `plan` — that was the whole point of it, pinning the value
-- so an account could not raise its own — and Postgres refuses to drop a column
-- a policy still references:
--
--   ERROR: cannot drop column plan of table profiles because other objects
--   depend on it
--
-- `drop ... cascade` would also work and is the wrong tool: it would take the
-- policy with it silently and leave the table with no update policy at all,
-- which is not "no restriction" but "no updates allowed" — every client rename
-- of a display name would start failing, and nothing would say why.
drop policy if exists "update own profile" on public.profiles;

alter table public.profiles drop constraint if exists profiles_plan_check;
alter table public.profiles drop column if exists plan;

-- Recreated without the `plan` clause, which had nothing left to guard.
create policy "update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

commit;

-- PostgREST caches the schema and will keep answering for functions that are
-- gone until it is told otherwise.
notify pgrst, 'reload schema';

-- --- Afterwards -------------------------------------------------------------
--
-- 1. Rotate `SUPABASE_SERVICE_ROLE_KEY`. Nothing in this project uses it any
--    more — the backend reached the credit functions with it and there are no
--    credit functions — so it is now a key that bypasses row-level security and
--    protects nothing. Rotate it in Settings → API and delete it from Render.
--
-- 2. Cancel the Razorpay webhook, in Razorpay's dashboard → Settings →
--    Webhooks. `/v1/billing/webhook` no longer exists; left in place it retries
--    every event against a 404 until it gives up.
--
-- 3. Cancel any live Razorpay subscriptions, or they keep charging people for
--    a plan this backend can no longer see. Subscriptions → filter by active.

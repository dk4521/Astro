-- Kosmiq — Supabase schema
--
-- Run this in the SQL editor of a fresh project. It creates the five tables the
-- app syncs into, and locks every one of them to its owner.
--
-- Birth details are the most personal thing this product holds: a date, a
-- minute and a place is enough to identify someone. So row-level security is
-- not a later hardening step here, it is part of the table definition — a
-- Supabase anon key is public by design, and without RLS these tables are a
-- public API over everyone's birth data.

-- --- Profiles ---------------------------------------------------------------
-- One row per account, created automatically on sign-up.

create table if not exists public.profiles (
  id          uuid primary key references auth.users on delete cascade,
  display_name text,
  -- What the account is allowed. 'free' until something upstream says
  -- otherwise; nothing in the app writes this column, and the RLS policy below
  -- deliberately does not let it: a client that can raise its own plan is not a
  -- plan, it is a suggestion.
  plan        text not null default 'free' check (plan in ('free', 'paid')),
  created_at  timestamptz not null default now()
);

-- For projects created before the column existed.
alter table public.profiles add column if not exists plan text not null default 'free';

alter table public.profiles enable row level security;

drop policy if exists "read own profile" on public.profiles;
create policy "read own profile"
  on public.profiles for select using (auth.uid() = id);

-- `display_name` is the only column a client has any business changing. The
-- check below is what keeps `plan` out of reach: an update that alters it fails
-- rather than silently upgrading the account that asked.
drop policy if exists "update own profile" on public.profiles;
create policy "update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id and plan = (select plan from public.profiles where id = auth.uid()));

-- Supabase does not create a profile row for you; this trigger does.
create or replace function public.handle_new_user()
returns trigger
language plpgsql
security definer set search_path = ''
as $$
begin
  insert into public.profiles (id) values (new.id);
  return new;
end;
$$;

drop trigger if exists on_auth_user_created on auth.users;
create trigger on_auth_user_created
  after insert on auth.users
  for each row execute function public.handle_new_user();


-- --- Charts -----------------------------------------------------------------
-- The birth details themselves. Not the computed chart: that is a pure function
-- of these five values, so storing the output would only create a second copy
-- to fall out of date when the engine improves.

create table if not exists public.charts (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  label      text,
  birth_date date not null,
  birth_time time not null,
  latitude   double precision not null check (latitude between -90 and 90),
  longitude  double precision not null check (longitude between -180 and 180),
  place      text,
  timezone   text,
  is_primary boolean not null default false,
  created_at timestamptz not null default now()
);

create index if not exists charts_user_idx on public.charts (user_id);

-- One primary chart per account: the one the app opens with.
create unique index if not exists charts_one_primary
  on public.charts (user_id) where is_primary;

alter table public.charts enable row level security;

drop policy if exists "read own charts" on public.charts;
create policy "read own charts"   on public.charts for select using (auth.uid() = user_id);
drop policy if exists "insert own charts" on public.charts;
create policy "insert own charts" on public.charts for insert with check (auth.uid() = user_id);
drop policy if exists "update own charts" on public.charts;
create policy "update own charts" on public.charts for update using (auth.uid() = user_id);
drop policy if exists "delete own charts" on public.charts;
create policy "delete own charts" on public.charts for delete using (auth.uid() = user_id);


-- --- Course progress --------------------------------------------------------
-- Which chapters have been read. One row per chapter rather than an array, so
-- two devices finishing different chapters merge instead of overwriting.

create table if not exists public.course_progress (
  user_id   uuid not null references auth.users on delete cascade,
  slug      text not null,
  read_at   timestamptz not null default now(),
  primary key (user_id, slug)
);

alter table public.course_progress enable row level security;

drop policy if exists "read own progress" on public.course_progress;
create policy "read own progress"   on public.course_progress for select using (auth.uid() = user_id);
drop policy if exists "insert own progress" on public.course_progress;
create policy "insert own progress" on public.course_progress for insert with check (auth.uid() = user_id);
drop policy if exists "delete own progress" on public.course_progress;
create policy "delete own progress" on public.course_progress for delete using (auth.uid() = user_id);


-- --- Conversations ----------------------------------------------------------
-- Chat history. Nothing here is generated by the app's engine, so unlike a
-- chart it cannot be recomputed — which is exactly why it needs storing.

create table if not exists public.conversations (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  chart_id   uuid references public.charts on delete set null,
  language   text not null default 'hinglish',
  -- Who the conversation was with. Switching companion starts a new row rather
  -- than continuing this one, so the history screen can say whose thread it is
  -- reading back. Nullable for rows written before companions existed.
  persona    text,
  created_at timestamptz not null default now()
);

-- For projects created before the column existed.
alter table public.conversations add column if not exists persona text;

create table if not exists public.messages (
  id              uuid primary key default gen_random_uuid(),
  conversation_id uuid not null references public.conversations on delete cascade,
  user_id         uuid not null references auth.users on delete cascade,
  role            text not null check (role in ('user', 'assistant')),
  content         text not null,
  -- The grounding verdict travels with the message it describes. A reading
  -- that disagreed with the chart must still say so when it is read back.
  grounded        boolean,
  contradictions  text[],
  created_at      timestamptz not null default now()
);

create index if not exists messages_conversation_idx
  on public.messages (conversation_id, created_at);

alter table public.conversations enable row level security;
alter table public.messages enable row level security;

drop policy if exists "read own conversations" on public.conversations;
create policy "read own conversations"   on public.conversations for select using (auth.uid() = user_id);
drop policy if exists "insert own conversations" on public.conversations;
create policy "insert own conversations" on public.conversations for insert with check (auth.uid() = user_id);
-- `language` is the one mutable column here: the reading screen switches
-- language mid-thread, so the row has to be able to follow. Without this policy
-- the update is not rejected, it simply matches no row — a silent no-op that
-- leaves the column quietly claiming a language the conversation stopped being
-- held in. Found by running the sync layer against a real project, not by
-- reading the schema.
drop policy if exists "update own conversations" on public.conversations;
create policy "update own conversations" on public.conversations for update using (auth.uid() = user_id);
drop policy if exists "delete own conversations" on public.conversations;
create policy "delete own conversations" on public.conversations for delete using (auth.uid() = user_id);

drop policy if exists "read own messages" on public.messages;
create policy "read own messages"   on public.messages for select using (auth.uid() = user_id);
drop policy if exists "insert own messages" on public.messages;
create policy "insert own messages" on public.messages for insert with check (auth.uid() = user_id);
drop policy if exists "delete own messages" on public.messages;
create policy "delete own messages" on public.messages for delete using (auth.uid() = user_id);

-- PostgREST keeps its own picture of the schema and will answer PGRST202
-- ("could not find the function ... in the schema cache") for a function it has
-- not been told about, even once the function exists. This is the line that
-- tells it.
notify pgrst, 'reload schema';


-- ===========================================================================
-- Credits
-- ===========================================================================
--
-- One currency for everything. A message costs one credit, and credits arrive
-- from three places that differ only in how long they last:
--
--   free          6 a day, expiring at the next Indian midnight
--   subscription  a month's worth, expiring at the end of the paid period
--   pack          bought outright, expiring in a year
--
-- That uniformity is the whole point of the design. The alternative — a daily
-- limit for subscribers plus a separate top-up balance — needs two counters,
-- two exhaustion messages and a rule about which drains first. Here the rule
-- falls out of the data: spend the credits that expire soonest, and a free
-- allowance is simply the lot that expires tonight.
--
-- Nothing in this section is writable by a client. The functions that create
-- and spend credits are `security definer` and have their execute permission
-- revoked from `anon` and `authenticated` below; the backend calls them with
-- the service-role key, having verified who is asking. A client that could
-- grant itself credits would not be a currency, it would be a suggestion.

-- --- Lots -------------------------------------------------------------------
-- Credits are stored as lots rather than a single balance column. A balance is
-- one number and cannot answer the two questions that matter: when do these
-- expire, and where did they come from. A lot answers both, and makes refunds
-- and disputes a matter of reading rows rather than reconstructing arithmetic.

create table if not exists public.credit_lots (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  credits    integer not null check (credits > 0),
  remaining  integer not null check (remaining >= 0),
  source     text not null check (source in ('free', 'pack', 'subscription', 'gift', 'refund')),
  -- The idempotency key, and the reason a webhook can fire twice without
  -- paying twice: 'pay:<razorpay_payment_id>' for a purchase,
  -- 'free:2026-08-23' for a daily grant, 'sub:<id>:2026-08' for a month of
  -- subscription. The unique index below is what actually enforces it.
  source_ref text not null,
  -- Null means never. Used by packs, which a person has paid for outright.
  expires_at timestamptz,
  created_at timestamptz not null default now(),
  constraint credit_lots_remaining_fits check (remaining <= credits)
);

create unique index if not exists credit_lots_source_ref
  on public.credit_lots (user_id, source_ref);

-- The index the spend path walks: live lots for one account, soonest expiry
-- first. Partial, because a lot with nothing left in it is history.
create index if not exists credit_lots_live_idx
  on public.credit_lots (user_id, expires_at nulls last, created_at)
  where remaining > 0;

-- --- Spends -----------------------------------------------------------------
-- One row per credit actually spent. Not needed to compute the balance —
-- `remaining` on the lot already carries that — and kept anyway, because
-- "where did my credits go" is a question a paying person is entitled to ask
-- and a `remaining` column cannot answer.

create table if not exists public.credit_spends (
  id         uuid primary key default gen_random_uuid(),
  user_id    uuid not null references auth.users on delete cascade,
  lot_id     uuid not null references public.credit_lots on delete cascade,
  -- What the credit was spent on, and the second idempotency key in this file:
  -- a chat request that is retried after a dropped connection carries the same
  -- ref and must not be charged twice.
  ref        text not null,
  created_at timestamptz not null default now()
);

create unique index if not exists credit_spends_ref
  on public.credit_spends (user_id, ref);

create index if not exists credit_spends_user_idx
  on public.credit_spends (user_id, created_at desc);

-- --- Subscriptions ----------------------------------------------------------
-- What Razorpay says about a recurring plan. The credits it produces live in
-- `credit_lots` like any others; this table exists to answer "is it still
-- running, and until when", which lots cannot say once they are spent.

create table if not exists public.subscriptions (
  id                 uuid primary key default gen_random_uuid(),
  user_id            uuid not null references auth.users on delete cascade,
  plan               text not null check (plan in ('monthly', 'yearly')),
  -- Razorpay's own vocabulary, kept rather than translated: created, authenticated,
  -- active, pending, halted, cancelled, completed, expired. Translating it here
  -- would mean guessing at states we have not seen yet.
  status             text not null,
  provider           text not null default 'razorpay',
  provider_id        text not null,
  current_period_end timestamptz,
  created_at         timestamptz not null default now(),
  updated_at         timestamptz not null default now()
);

create unique index if not exists subscriptions_provider_id
  on public.subscriptions (provider, provider_id);

-- At most one live subscription per account. Someone who upgrades monthly to
-- yearly gets the old row moved out of these states first.
create unique index if not exists subscriptions_one_live
  on public.subscriptions (user_id)
  where status in ('created', 'authenticated', 'active', 'pending', 'halted');

-- --- Payments ---------------------------------------------------------------
-- Every settled payment, for reconciliation against the Razorpay dashboard.
-- Deliberately separate from `credit_lots`: a payment that arrived but whose
-- credits failed to grant must be visible as exactly that, not absent.

create table if not exists public.payments (
  id                  uuid primary key default gen_random_uuid(),
  user_id             uuid not null references auth.users on delete cascade,
  provider            text not null default 'razorpay',
  provider_payment_id text not null,
  provider_order_id   text,
  product             text not null,
  amount_paise        integer not null,
  currency            text not null default 'INR',
  status              text not null,
  created_at          timestamptz not null default now()
);

create unique index if not exists payments_provider_payment_id
  on public.payments (provider, provider_payment_id);

create index if not exists payments_user_idx
  on public.payments (user_id, created_at desc);

-- --- Row-level security -----------------------------------------------------
-- Read your own, write nothing. There is no insert or update policy anywhere in
-- this section on purpose: every write goes through a `security definer`
-- function called by the backend, which is the only party that has seen a
-- Razorpay signature.

alter table public.credit_lots   enable row level security;
alter table public.credit_spends enable row level security;
alter table public.subscriptions enable row level security;
alter table public.payments      enable row level security;

drop policy if exists "read own lots" on public.credit_lots;
create policy "read own lots" on public.credit_lots for select using (auth.uid() = user_id);

drop policy if exists "read own spends" on public.credit_spends;
create policy "read own spends" on public.credit_spends for select using (auth.uid() = user_id);

drop policy if exists "read own subscriptions" on public.subscriptions;
create policy "read own subscriptions" on public.subscriptions for select using (auth.uid() = user_id);

drop policy if exists "read own payments" on public.payments;
create policy "read own payments" on public.payments for select using (auth.uid() = user_id);

-- And the writes, which are not a client's to make.
--
-- Every function below is `security definer`, so inside one the current role is
-- the function's owner rather than whoever called it. Row-level security still
-- applies to that role, and these tables have no insert or update policy — so
-- without the policies here, `ensure_free_grant` would be refused by the very
-- table it exists to write to.
--
-- Naming the roles explicitly rather than relying on `postgres` holding
-- BYPASSRLS: that is true on a Supabase project today and is not a property
-- this schema should depend on. `authenticated` and `anon` are not named, so
-- nothing changes for a client.

drop policy if exists "service writes lots" on public.credit_lots;
create policy "service writes lots" on public.credit_lots
  for all to postgres, service_role using (true) with check (true);

drop policy if exists "service writes spends" on public.credit_spends;
create policy "service writes spends" on public.credit_spends
  for all to postgres, service_role using (true) with check (true);

drop policy if exists "service writes subscriptions" on public.subscriptions;
create policy "service writes subscriptions" on public.subscriptions
  for all to postgres, service_role using (true) with check (true);

drop policy if exists "service writes payments" on public.payments;
create policy "service writes payments" on public.payments
  for all to postgres, service_role using (true) with check (true);

-- `profiles.plan` is mirrored from `subscriptions` by `record_subscription`.
-- The client's own update policy above still refuses to let it change `plan`;
-- this one applies to a different role and so does not loosen that.
drop policy if exists "service writes profiles" on public.profiles;
create policy "service writes profiles" on public.profiles
  for update to postgres, service_role using (true) with check (true);


-- --- The plan column --------------------------------------------------------
-- `profiles.plan` predates this section and used to be the whole billing
-- model: 'free' or 'paid'. It is now a cache of what `subscriptions` says,
-- kept because the app reads it on every screen and a join per screen is worse
-- than a column the backend maintains. It is still unwritable by a client —
-- the policy above sees to that — and it no longer decides anything: the
-- allowance comes from credits.

alter table public.profiles drop constraint if exists profiles_plan_check;
alter table public.profiles add constraint profiles_plan_check
  check (plan in ('free', 'paid', 'monthly', 'yearly'));


-- --- Reading the balance ----------------------------------------------------

-- The one place that decides what "a live credit" means. Every other function
-- here defers to it, so a change to expiry semantics happens once.
create or replace function public.credit_balance_of(p_user_id uuid)
returns integer
language sql
stable
security definer
set search_path = ''
as $$
  select coalesce(sum(l.remaining), 0)::integer
  from public.credit_lots l
  where l.user_id = p_user_id
    and l.remaining > 0
    and (l.expires_at is null or l.expires_at > now());
$$;

-- What the app asks for. One round trip, because the chat screen needs the
-- balance, what expires next and whether there is a subscription behind it —
-- and three queries to draw one line of text is three chances to disagree.
--
-- Calling this also mints today's free credits if they are missing, so the
-- screen that reads the balance is the screen that creates it. There is no
-- scheduled job to forget to deploy.
create or replace function public.credit_summary()
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_user uuid := auth.uid();
  v_next timestamptz;
  v_sub  record;
begin
  if v_user is null then
    return jsonb_build_object('balance', 0, 'plan', 'free', 'signed_in', false);
  end if;

  perform public.ensure_grants(v_user);

  select min(l.expires_at) into v_next
  from public.credit_lots l
  where l.user_id = v_user
    and l.remaining > 0
    and l.expires_at is not null
    and l.expires_at > now();

  select s.plan, s.status, s.current_period_end into v_sub
  from public.subscriptions s
  where s.user_id = v_user
    and s.status in ('active', 'authenticated', 'pending', 'halted')
  order by s.created_at desc
  limit 1;

  return jsonb_build_object(
    'signed_in',   true,
    'balance',     public.credit_balance_of(v_user),
    'expires_at',  v_next,
    'plan',        coalesce(v_sub.plan, 'free'),
    'status',      v_sub.status,
    'period_end',  v_sub.current_period_end
  );
end;
$$;


-- --- Granting ---------------------------------------------------------------

-- The daily free lot: six credits that expire at the next Indian midnight.
--
-- India is hard-coded rather than read from the account because the product is
-- one country and a per-user timezone here would mean a person who travels
-- gets a short day or a long one. `on conflict do nothing` is what makes this
-- safe to call on every balance read — the unique index on (user_id,
-- source_ref) is the thing doing the work, not a prior existence check, which
-- would race with itself under concurrent requests.
create or replace function public.ensure_free_grant(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_today date := (now() at time zone 'Asia/Kolkata')::date;
begin
  insert into public.credit_lots (user_id, credits, remaining, source, source_ref, expires_at)
  values (
    p_user_id, 6, 6, 'free', 'free:' || v_today::text,
    ((v_today + 1)::timestamp at time zone 'Asia/Kolkata')
  )
  on conflict (user_id, source_ref) do nothing;
end;
$$;

-- A month of subscription credits.
--
-- Why this is a function of reading the balance rather than a scheduled job:
-- a yearly subscriber is charged once, so Razorpay sends one
-- `subscription.charged` webhook a year. Granting the whole year at signup
-- would hand someone 18,000 credits to spend in a week; granting monthly needs
-- something to happen on the first of the month, and the cheapest reliable
-- "something" is the next time that person opens the app. Nothing to deploy,
-- nothing to forget, and a person who does not open the app does not need the
-- credits meanwhile.
--
-- A subscription that starts mid-month gets that month's full grant and the
-- next month's on the 1st. That is a few days of bonus, deliberately: the
-- alternative is prorating, which turns "1,500 credits a month" into a
-- sentence nobody can check.
--
-- The 1500 below is mirrored in backend/app/billing/plans.py, which is where
-- the price beside it is written. The two must agree.
create or replace function public.ensure_subscription_grant(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_sub   record;
  v_local timestamp := (now() at time zone 'Asia/Kolkata');
  v_month text      := to_char(v_local, 'YYYY-MM');
begin
  select s.plan, s.provider_id, s.current_period_end into v_sub
  from public.subscriptions s
  where s.user_id = p_user_id and s.status = 'active'
  order by s.created_at desc
  limit 1;

  if v_sub.provider_id is null then
    return;
  end if;

  insert into public.credit_lots (user_id, credits, remaining, source, source_ref, expires_at)
  values (
    p_user_id, 1500, 1500, 'subscription',
    'sub:' || v_sub.provider_id || ':' || v_month,
    least(
      ((date_trunc('month', v_local) + interval '1 month') at time zone 'Asia/Kolkata'),
      coalesce(v_sub.current_period_end, 'infinity'::timestamptz)
    )
  )
  on conflict (user_id, source_ref) do nothing;
end;
$$;

-- Everything this account is owed right now. The single call the read and
-- spend paths make, so neither has to know how many kinds of grant exist.
create or replace function public.ensure_grants(p_user_id uuid)
returns void
language plpgsql
security definer
set search_path = ''
as $$
begin
  perform public.ensure_free_grant(p_user_id);
  perform public.ensure_subscription_grant(p_user_id);
end;
$$;

-- Add credits from anything that is not the daily grant. Returns the lot, or
-- null when `source_ref` has been seen before — which is the normal outcome of
-- a webhook Razorpay decided to deliver twice, not an error.
create or replace function public.grant_credits(
  p_user_id    uuid,
  p_credits    integer,
  p_source     text,
  p_source_ref text,
  p_expires_at timestamptz default null
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id uuid;
begin
  insert into public.credit_lots (user_id, credits, remaining, source, source_ref, expires_at)
  values (p_user_id, p_credits, p_credits, p_source, p_source_ref, p_expires_at)
  on conflict (user_id, source_ref) do nothing
  returning id into v_id;

  return v_id;
end;
$$;


-- --- Spending ---------------------------------------------------------------

-- Take one credit, from the lot that expires soonest.
--
-- Three things here are not decoration:
--
--   The spend is recorded and the lot decremented in one statement pair inside
--   one function, so a balance can never be charged without a row saying why.
--
--   `p_ref` makes the call idempotent. A chat request whose connection drops
--   and is retried carries the same ref, and the second call returns the same
--   answer instead of charging again.
--
--   `for update skip locked` is the concurrency choice. Two requests from the
--   same account arriving together must not both wait on the same lot; the
--   second one skips to the next lot and spends there. Under contention that
--   costs a slightly wrong spend order, which is worth strictly less than the
--   deadlock it avoids.
create or replace function public.consume_credit(p_user_id uuid, p_ref text)
returns jsonb
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_lot uuid;
begin
  if exists (
    select 1 from public.credit_spends s
    where s.user_id = p_user_id and s.ref = p_ref
  ) then
    return jsonb_build_object(
      'ok', true, 'replayed', true, 'balance', public.credit_balance_of(p_user_id)
    );
  end if;

  perform public.ensure_grants(p_user_id);

  select l.id into v_lot
  from public.credit_lots l
  where l.user_id = p_user_id
    and l.remaining > 0
    and (l.expires_at is null or l.expires_at > now())
  order by l.expires_at asc nulls last, l.created_at asc
  for update skip locked
  limit 1;

  if v_lot is null then
    return jsonb_build_object('ok', false, 'replayed', false, 'balance', 0);
  end if;

  update public.credit_lots set remaining = remaining - 1 where id = v_lot;
  insert into public.credit_spends (user_id, lot_id, ref) values (p_user_id, v_lot, p_ref);

  return jsonb_build_object(
    'ok', true, 'replayed', false, 'balance', public.credit_balance_of(p_user_id)
  );
end;
$$;

-- Give a credit back, for a request that was charged and then failed on our
-- side. Returning it to the lot it came from rather than minting a new one
-- keeps the expiry honest: a refunded free credit still dies tonight.
create or replace function public.refund_credit(p_user_id uuid, p_ref text)
returns boolean
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_lot uuid;
begin
  delete from public.credit_spends s
  where s.user_id = p_user_id and s.ref = p_ref
  returning s.lot_id into v_lot;

  if v_lot is null then
    return false;
  end if;

  update public.credit_lots
  set remaining = least(remaining + 1, credits)
  where id = v_lot;

  return true;
end;
$$;


-- --- Subscriptions and payments, written by the webhook ---------------------

-- Record what Razorpay says about a subscription and mirror it onto
-- `profiles.plan`.
--
-- The status vocabulary is Razorpay's, and the set of states that count as
-- "paying" is named once, here. A subscription in `halted` — a mandate that
-- failed to debit — is deliberately included in the live index but not treated
-- as paid: the person keeps whatever credits they were already granted, and
-- gets no new month until the payment succeeds.
create or replace function public.record_subscription(
  p_user_id     uuid,
  p_plan        text,
  p_status      text,
  p_provider_id text,
  p_period_end  timestamptz default null
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id   uuid;
  v_live constant text[] := array['created', 'authenticated', 'active', 'pending', 'halted'];
begin
  -- Someone who moves from monthly to yearly has two subscriptions at
  -- Razorpay for a moment, and `subscriptions_one_live` allows only one here.
  -- Without this the second one's insert fails on that index and the webhook
  -- 500s forever, which is a purchase that never becomes credits.
  --
  -- The old row is marked superseded rather than cancelled, because those are
  -- different facts: cancelled means Razorpay was told to stop, superseded
  -- means this app stopped counting it. Cancelling the old mandate is the
  -- app's job, through /v1/billing/cancel, and it is not done silently here.
  if p_status = any (v_live) then
    update public.subscriptions
    set status = 'superseded', updated_at = now()
    where user_id = p_user_id
      and provider_id is distinct from p_provider_id
      and status = any (v_live);
  end if;

  insert into public.subscriptions (user_id, plan, status, provider_id, current_period_end)
  values (p_user_id, p_plan, p_status, p_provider_id, p_period_end)
  on conflict (provider, provider_id) do update
    set status             = excluded.status,
        current_period_end = coalesce(excluded.current_period_end, public.subscriptions.current_period_end),
        updated_at         = now()
  returning id into v_id;

  update public.profiles
  set plan = case when p_status = 'active' then p_plan else 'free' end
  where id = p_user_id;

  return v_id;
end;
$$;

-- One settled payment. Separate from the credits it buys so that money
-- arriving and credits appearing are two facts that can be compared.
create or replace function public.record_payment(
  p_user_id     uuid,
  p_payment_id  text,
  p_order_id    text,
  p_product     text,
  p_amount      integer,
  p_status      text
)
returns uuid
language plpgsql
security definer
set search_path = ''
as $$
declare
  v_id uuid;
begin
  insert into public.payments (user_id, provider_payment_id, provider_order_id, product, amount_paise, status)
  values (p_user_id, p_payment_id, p_order_id, p_product, p_amount, p_status)
  on conflict (provider, provider_payment_id) do update
    set status = excluded.status
  returning id into v_id;

  return v_id;
end;
$$;


-- --- Who may call what ------------------------------------------------------
--
-- The most important lines in this file. PostgreSQL grants `execute` on a new
-- function to `public` by default, and a `security definer` function runs as
-- its owner — so without these revokes, `grant_credits` would be a public API
-- for minting money, reachable from any device holding the anon key.
--
-- Only `credit_summary` survives for clients, and it reads.

revoke execute on function public.credit_balance_of(uuid)                        from public, anon, authenticated;
revoke execute on function public.ensure_free_grant(uuid)                        from public, anon, authenticated;
revoke execute on function public.ensure_subscription_grant(uuid)                from public, anon, authenticated;
revoke execute on function public.ensure_grants(uuid)                            from public, anon, authenticated;
revoke execute on function public.grant_credits(uuid, integer, text, text, timestamptz) from public, anon, authenticated;
revoke execute on function public.consume_credit(uuid, text)                     from public, anon, authenticated;
revoke execute on function public.refund_credit(uuid, text)                      from public, anon, authenticated;
revoke execute on function public.record_subscription(uuid, text, text, text, timestamptz) from public, anon, authenticated;
revoke execute on function public.record_payment(uuid, text, text, text, integer, text)    from public, anon, authenticated;

-- The service role bypasses row-level security but not function permissions,
-- so it has to be named.
grant execute on function public.credit_balance_of(uuid)                         to service_role;
grant execute on function public.ensure_free_grant(uuid)                         to service_role;
grant execute on function public.ensure_subscription_grant(uuid)                 to service_role;
grant execute on function public.ensure_grants(uuid)                             to service_role;
grant execute on function public.grant_credits(uuid, integer, text, text, timestamptz)  to service_role;
grant execute on function public.consume_credit(uuid, text)                      to service_role;
grant execute on function public.refund_credit(uuid, text)                       to service_role;
grant execute on function public.record_subscription(uuid, text, text, text, timestamptz) to service_role;
grant execute on function public.record_payment(uuid, text, text, text, integer, text)    to service_role;

grant execute on function public.credit_summary() to authenticated;

notify pgrst, 'reload schema';

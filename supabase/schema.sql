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

-- There is no `plan` column any more. It used to say 'free' or 'paid' and was
-- a cache of what the `subscriptions` table said; both are gone. What someone
-- has paid for is RevenueCat's answer to give, and a copy of it in a row a
-- client can read is a copy that can be stale, and eventually a copy someone
-- tries to write. See the note at the foot of this file.
create table if not exists public.profiles (
  id           uuid primary key references auth.users on delete cascade,
  display_name text,
  created_at   timestamptz not null default now()
);

alter table public.profiles enable row level security;

drop policy if exists "read own profile" on public.profiles;
create policy "read own profile"
  on public.profiles for select using (auth.uid() = id);

-- `display_name` is now the only column a client could change, so the policy is
-- just ownership. The `with check` used to also pin `plan` to its current value,
-- because an account that can raise its own plan is not a plan, it is a
-- suggestion. That clause left with the column it was guarding.
drop policy if exists "update own profile" on public.profiles;
create policy "update own profile"
  on public.profiles for update
  using (auth.uid() = id)
  with check (auth.uid() = id);

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

-- ===========================================================================
-- What is no longer here
-- ===========================================================================
--
-- `credit_lots`, `credit_spends`, `subscriptions`, `payments`, and the nine
-- functions that granted, spent, refunded and reported credits. Also
-- `profiles.plan`, which was a cache of what `subscriptions` said.
--
-- **Why it went.** The ledger sold a currency: six free a day, packs bought
-- outright, a month's worth from a subscription, spent one message at a time.
-- It was undone by the thing that made it convenient. `consume_credit` took an
-- idempotency key so that a question whose stream died could be re-asked for
-- free — and the key came from the client, and a repeat was answered "already
-- paid, carry on". One fixed `request_id`, sent forever, therefore cost exactly
-- one credit ever. A modified app had unlimited paid messages for ₹19.
--
-- The fix is not a better key. It is that a subscription is not a currency:
-- there is nothing to meter, so there is nothing to replay. The product now
-- sells access, RevenueCat holds the record of who has it, and the backend asks
-- RevenueCat rather than counting anything itself (`backend/app/entitlements.py`).
--
-- **What replaced the free six a day.** The split moved from "how many messages"
-- to "which features". Everything this engine computes without a model — chart,
-- panchang, dasha, matching, the tarot draw, the course — is free and needs no
-- account at all. Every sentence a model writes is Pro. That is a line a person
-- can hold in their head, which the old one never was.
--
-- **To remove the ledger from a project that already ran the old schema**, use
-- `migrations/2026-09-01-drop-credits.sql`. It drops the tables and takes the
-- payment history with them, so read the note at the top of it first. Running
-- *this* file on an old project does not remove anything — it only stops
-- creating it.

-- PostgREST keeps its own picture of the schema and will answer PGRST202
-- ("could not find the function ... in the schema cache") for a function it has
-- not been told about, even once the function exists. This is the line that
-- tells it.
notify pgrst, 'reload schema';

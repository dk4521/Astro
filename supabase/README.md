# Supabase setup

## 1. Create the project

Any region; the free tier is enough to start. Copy the **Project URL** and the
**anon public** key from Settings → API.

## 2. Run the schema

Paste [schema.sql](schema.sql) into the SQL editor and run it. It creates
`profiles`, `charts`, `course_progress`, `conversations` and `messages`, the
credit tables (`credit_lots`, `credit_spends`, `subscriptions`, `payments`),
and enables row-level security on all of them.

**The whole file is re-runnable, including the policies** — each is dropped
before it is created. Run it again whenever the schema changes; there is no
separate migration to hunt for.

That was not true at first. `create policy` refuses to duplicate, so re-running
the file on a live project failed on the very first policy with `42710: policy
"read own profile" for table "profiles" already exists` and nothing after it
ran. If you hit that error on an older copy of this file, take a newer one.

**Do not skip the RLS policies.** The anon key ships inside the app and is meant
to be public; without those policies these tables are an open API over everyone's
birth details.

**Do not skip the `revoke execute` lines at the end either.** PostgreSQL grants
`execute` on a new function to `public` by default, and the credit functions are
`security definer` — they run as their owner. Without those revokes,
`grant_credits` is a public API for minting money, reachable from any device
holding the anon key. Only `credit_summary`, which reads, stays available to a
signed-in client.

After running it, one query is worth pasting to confirm the revokes took:

```sql
select p.proname, has_function_privilege('authenticated', p.oid, 'execute') as client_can_call
from pg_proc p join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.proname in (
  'grant_credits','consume_credit','refund_credit','ensure_grants',
  'record_payment','record_subscription','credit_summary'
) order by 1;
```

Everything must read `false` except `credit_summary`.

## 3. Point the app at it

Create `mobile/.env` (git-ignored):

```
EXPO_PUBLIC_SUPABASE_URL=https://xxxxxxxx.supabase.co
EXPO_PUBLIC_SUPABASE_ANON_KEY=eyJhbGciOi...
```

Restart `npx expo start` — env vars are read at bundle time, so a running
packager will not pick them up.

Without these the app still runs. Accounts simply do not appear, and everything
stays on the device, which is how it worked before auth existed.

## 4. Give the backend a service-role key

Billing is the one thing the app cannot do for itself. Copy the **service_role**
key from Settings → API into `backend/.env`:

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
SUPABASE_SERVICE_ROLE_KEY=eyJhbGciOi...
```

The service-role key bypasses row-level security. It belongs on the server and
nowhere else — never in an `EXPO_PUBLIC_` variable, never in a build. If it has
ever been in a client bundle, rotate it.

Without it the backend reports `billing.credits: false` at `/health`, `/v1/chat`
stays open to anyone who can reach it, and the pricing screen has nothing to
sell. That is the right behaviour for local development and the wrong one for
anything public — `/health` is where to check which of the three switches
(`accounts`, `credits`, `payments`) are actually on.

## 5. For testing, consider turning email confirmation off

Authentication → Providers → Email → **Confirm email**. With it on (the default)
a new sign-up gets a user but no session until the link is clicked; the sign-up
screen says so rather than appearing to hang. Turn it back on before launch.

## What syncs, and what the device still owns

The device remains the source of truth for reading. Every screen loads from
AsyncStorage exactly as it did before accounts existed, so the app works signed
out, offline, and in a build with no project configured at all. Supabase is a
mirror: it fills that local store on a new phone and receives changes as they
happen. See `mobile/src/sync/`.

| Table | Direction | Merge rule |
| --- | --- | --- |
| `charts` | both ways | Newest edit wins, compared by timestamp. Changing your details inserts a new row and demotes the old one, so an old conversation stays attached to the chart it was about |
| `course_progress` | both ways | Union. Two devices reading different chapters add up rather than overwrite |
| `conversations` / `messages` | up, read back on open | Append-only. The grounding verdict is stored with the message it describes |
| `credit_lots` / `credit_spends` | server only | Written by `security definer` functions the backend calls with the service-role key. The app reads its balance through `credit_summary()` and can write nothing |
| `profiles` | created by trigger | — |

There is no queue of pending writes, deliberately. Every merge is a union or a
timestamp comparison, so running it twice does what running it once did, and a
push that failed in a tunnel is simply noticed as missing by the next pass.

The opening reading is **not** stored. It is generated fresh from the chart in
whichever language is selected, so a saved copy would only be a stale duplicate.

## Checked against a real project

The sync layer was exercised end to end against a live Supabase project rather
than reasoned about: chart insert and round trip, the demote-then-insert path
under the `charts_one_primary` unique index, the union upsert, conversation and
message storage including the grounding verdict, the cascade on delete, and RLS
refusing a signed-out client both reads and writes. That run is what turned up
the missing `update` policy above.

# Supabase setup

## 1. Create the project

Any region; the free tier is enough to start. Copy the **Project URL** and the
**anon public** key from Settings → API.

## 2. Run the schema

Paste [schema.sql](schema.sql) into the SQL editor and run it. It creates
`profiles`, `charts`, `course_progress`, `conversations` and `messages`, and
enables row-level security on all of them.

**Upgrading a project that ran an older copy?** The credit tables are gone —
what someone has paid for is RevenueCat's answer now, not a balance in this
database. Running the current schema.sql does not remove the old objects, it
only stops creating them; use
[migrations/2026-09-01-drop-credits.sql](migrations/2026-09-01-drop-credits.sql)
to drop them, and read the warning at the top of it first, because it takes the
Razorpay payment history with it.

**Upgrading a project created before 2 September 2026?** It has no
`delete_own_account()`, so Settings → *Delete account* answers `PGRST202` and
the app cannot offer the deletion route both stores require. Run
[migrations/2026-09-02-account-deletion.sql](migrations/2026-09-02-account-deletion.sql);
it creates the function and destroys nothing. Then call it once from a signed-in
test account and check the row is gone — on some projects `postgres` cannot
write to `auth.users`, and the file's last line says what to do about that.

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

**If you ever add a `security definer` function, revoke it first.** PostgreSQL
grants `execute` on a new function to `public` by default, and a `security
definer` function runs as its owner — so a forgotten revoke turns one into a
public API with the owner's privileges, reachable from any device holding the
anon key. The credit functions that needed this are gone and the current schema
defines none, which is why the file no longer ends in a wall of revokes. The
rule outlives them.

This is the query that says whether a client can call something it should not:

```sql
select p.proname, has_function_privilege('authenticated', p.oid, 'execute') as client_can_call
from pg_proc p
join pg_namespace n on n.oid = p.pronamespace
where n.nspname = 'public' and p.prosecdef
order by 1;
```

`handle_new_user` is the only row expected, and it is a trigger function rather
than anything a client can reach.

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

## 4. Let the backend verify who is asking

The backend needs to read the name on a token, and nothing more. The **anon**
key is enough for that:

```
SUPABASE_URL=https://xxxxxxxx.supabase.co
SUPABASE_ANON_KEY=eyJhbGciOi...
```

**No service-role key.** There used to be one here, because the backend wrote
the credit ledger with it. There is no ledger, so there is nothing on this
project the server needs to write, and a key that bypasses row-level security
is not worth holding for a job that does not exist. If your `backend/.env` still
has `SUPABASE_SERVICE_ROLE_KEY`, delete the line and rotate the key in
Settings → API — including from Render's dashboard.

What someone has *paid for* is a separate question with a separate key, and it
is not Supabase's: see `REVENUECAT_SECRET_KEY` in `backend/.env.example`.

Without the two variables above, nobody can be identified and every AI endpoint
answers whoever reaches it. That is the right behaviour for local development
and the wrong one for anything public. The server says which switches are off in
its startup log — `/health` deliberately does not, because that was an
unauthenticated answer to "is the paywall on".

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
| `profiles` | created by trigger | — |

Subscriptions are not in that table, and are not in this database at all. The
store took the payment, RevenueCat holds the record, and the backend asks
RevenueCat. A copy here would be a copy that can go stale — and eventually one
somebody tries to write.

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

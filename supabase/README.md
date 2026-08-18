# Supabase setup

## 1. Create the project

Any region; the free tier is enough to start. Copy the **Project URL** and the
**anon public** key from Settings → API.

## 2. Run the schema

Paste [schema.sql](schema.sql) into the SQL editor and run it. It creates
`profiles`, `charts`, `course_progress`, `conversations` and `messages`, and
enables row-level security on all of them.

Every statement is written to be re-runnable except the policies, which
`create policy` will refuse to duplicate. On a project created before the sync
layer existed, run this one addition instead of the whole file:

```sql
create policy "update own conversations"
  on public.conversations for update using (auth.uid() = user_id);
```

Without it the app still works — a conversation simply keeps recording the
language it was started in, because an update that matches no row under RLS is
a silent no-op rather than an error.

**Do not skip the RLS policies.** The anon key ships inside the app and is meant
to be public; without those policies these tables are an open API over everyone's
birth details.

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

## 4. For testing, consider turning email confirmation off

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

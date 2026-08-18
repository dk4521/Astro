# Supabase setup

## 1. Create the project

Any region; the free tier is enough to start. Copy the **Project URL** and the
**anon public** key from Settings → API.

## 2. Run the schema

Paste [schema.sql](schema.sql) into the SQL editor and run it. It creates
`profiles`, `charts`, `course_progress`, `conversations` and `messages`, and
enables row-level security on all of them.

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

## What is not wired yet

The tables exist and the app authenticates, but nothing syncs into them: birth
details and course progress are still device-local, and chat history is not
stored at all. That is the next piece of work, and the schema above is the shape
it should write into.

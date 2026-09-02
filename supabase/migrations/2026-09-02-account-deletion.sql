-- Let an account delete itself.
--
-- Run this once, in the SQL editor, on a project created before today. A
-- project created from the current `schema.sql` already has the function and
-- does not need this file.
--
-- Nothing here destroys any data by itself: it only creates the function that
-- Settings → Delete account calls, which is the route Google Play and the App
-- Store both require an app with accounts to provide. Until it exists, that
-- button answers PGRST202 — "could not find the function in the schema cache".

begin;

-- ===========================================================================
-- Deleting an account
-- ===========================================================================
--
-- Every table above hangs off `auth.users` with `on delete cascade`, so all of
-- someone's data is one delete — and that delete is the one thing a signed-in
-- client cannot do for itself. `auth.users` is not exposed through PostgREST at
-- all, and no policy can grant what is not reachable.
--
-- The alternative was a service-role key on the backend, held so that one
-- endpoint could call the admin API. That key bypasses row-level security on
-- every table for every user, and `backend/app/auth.py` deliberately stopped
-- accepting it. A `security definer` function is the smaller thing: it does
-- exactly this, to exactly the caller, and nothing else — there is no argument
-- to get wrong, because `auth.uid()` decides whose account goes.
--
-- `search_path` is emptied so nothing here resolves through a schema the caller
-- could plant an object in. That is why every name below is qualified.
--
-- Google Play and the App Store both require an in-app route to this, and
-- Settings → Delete account is what calls it.

create or replace function public.delete_own_account()
returns void
language plpgsql
security definer
set search_path = ''
as $$
declare
  uid uuid := auth.uid();
begin
  if uid is null then
    raise exception 'Not signed in.' using errcode = '28000';
  end if;

  -- One row. The cascades take the profile, the charts, the course progress,
  -- the conversations and every message with them.
  delete from auth.users where id = uid;
end;
$$;

-- Postgres grants EXECUTE to everyone by default, and "everyone" here includes
-- the anonymous role a signed-out phone uses.
revoke all on function public.delete_own_account() from public;
revoke all on function public.delete_own_account() from anon;
grant execute on function public.delete_own_account() to authenticated;

-- If calling this returns "permission denied for table users", this project is
-- one where `postgres` cannot write to `auth.users`. Hand the function to the
-- role that owns that table and it works unchanged:
--
--   alter function public.delete_own_account() owner to supabase_auth_admin;

commit;

-- PostgREST keeps its own picture of the schema and will not find a function it
-- has not been told about, even once the function exists. This is that line.
notify pgrst, 'reload schema';

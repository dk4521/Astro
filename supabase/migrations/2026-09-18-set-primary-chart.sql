-- Migration: Add atomic primary chart swap function

create or replace function public.set_primary_chart(new_chart_id uuid)
returns void
language plpgsql
security definer
as $$
begin
  update public.charts set is_primary = false where user_id = auth.uid() and is_primary = true;
  update public.charts set is_primary = true where id = new_chart_id and user_id = auth.uid();
end;
$$;

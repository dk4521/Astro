/**
 * Course progress, mirrored into the account.
 *
 * The merge is a union in both directions, and that single choice is what makes
 * this safe without a queue of pending writes. A phone that was offline when a
 * chapter was finished has that chapter locally; the next sync notices it is
 * missing upstream and sends it. Nothing has to be replayed in order, nothing
 * can be applied twice to any effect, and two devices reading different chapters
 * add up rather than overwriting each other.
 *
 * The one thing a union cannot express is a deletion, which is why resetting
 * progress deletes upstream explicitly instead of leaving the reset to be
 * undone by the next merge.
 */

import { supabase } from '../auth/client';

/** Which chapters the account has recorded as read. */
export async function fetchProgress(userId: string): Promise<string[]> {
  if (!supabase) return [];

  const { data, error } = await supabase
    .from('course_progress')
    .select('slug')
    .eq('user_id', userId);

  if (error) throw new Error(error.message);
  return (data ?? []).map((row: { slug: string }) => row.slug);
}

/**
 * Record chapters as read upstream.
 *
 * `(user_id, slug)` is the primary key, so re-sending a chapter is a no-op
 * rather than an error — `ignoreDuplicates` keeps the original `read_at` instead
 * of moving it forward every time a sync runs.
 */
export async function pushProgress(userId: string, slugs: string[]): Promise<void> {
  if (!supabase || slugs.length === 0) return;

  const { error } = await supabase
    .from('course_progress')
    .upsert(
      slugs.map((slug) => ({ user_id: userId, slug })),
      { onConflict: 'user_id,slug', ignoreDuplicates: true },
    );

  if (error) throw new Error(error.message);
}

export async function clearRemoteProgress(userId: string): Promise<void> {
  if (!supabase) return;

  const { error } = await supabase.from('course_progress').delete().eq('user_id', userId);
  if (error) throw new Error(error.message);
}

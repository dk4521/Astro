/**
 * The birth details, mirrored into the account.
 *
 * `public.charts` stores the five inputs, never the computed chart — the chart
 * is a pure function of them, so a stored copy would only be a second version to
 * go stale the next time the engine improves. Reading one back means casting it
 * again, which is the cheap half of the work.
 *
 * Changing your birth details inserts a new row and demotes the old one rather
 * than editing in place. The old chart is what an old conversation was about;
 * overwriting it would leave that history attached to a reading it never
 * discussed. The schema is built for several charts per account and exactly one
 * primary, which is the shape this produces.
 */

import { supabase } from '../auth/client';
import type { BirthDetails } from '../api/types';

type ChartRow = {
  id: string;
  birth_date: string;
  birth_time: string;
  latitude: number;
  longitude: number;
  place: string | null;
  timezone: string | null;
  created_at: string;
};

const COLUMNS = 'id, birth_date, birth_time, latitude, longitude, place, timezone, created_at';

export type RemoteChart = {
  id: string;
  birth: BirthDetails;
  /** Epoch ms, for deciding which copy of a chart is the newer one. */
  savedAt: number;
};

/**
 * Postgres hands back a `time` as HH:MM:SS. The app has used HH:MM everywhere
 * since onboarding, and the seconds are always zero because there is nowhere to
 * type them — so this is a formatting difference, not a loss of precision.
 */
function toClockTime(value: string): string {
  return value.slice(0, 5);
}

function rowToChart(row: ChartRow): RemoteChart {
  const savedAt = Date.parse(row.created_at);
  return {
    id: row.id,
    savedAt: Number.isFinite(savedAt) ? savedAt : 0,
    birth: {
      date: row.birth_date,
      time: toClockTime(row.birth_time),
      latitude: row.latitude,
      longitude: row.longitude,
      place: row.place,
      timezone: row.timezone,
    },
  };
}

/**
 * Whether two sets of birth details describe the same chart.
 *
 * Coordinates come from a fixed gazetteer and round-trip exactly, so the
 * tolerance is only insurance against float formatting on the way through JSON;
 * 1e-6° is about ten centimetres, far below anything that moves a cusp.
 *
 * `place` and `timezone` are deliberately not compared. One is a display label
 * and the other is resolved from the coordinates, so neither changes a single
 * computed number — treating a re-worded label as a new chart would orphan a
 * conversation for nothing.
 */
export function sameChart(a: BirthDetails, b: BirthDetails): boolean {
  return (
    a.date === b.date &&
    a.time === b.time &&
    Math.abs(a.latitude - b.latitude) < 1e-6 &&
    Math.abs(a.longitude - b.longitude) < 1e-6
  );
}

/** The account's current chart, or null when it has none yet. */
export async function fetchPrimaryChart(userId: string): Promise<RemoteChart | null> {
  if (!supabase) return null;

  const { data, error } = await supabase
    .from('charts')
    .select(COLUMNS)
    .eq('user_id', userId)
    .eq('is_primary', true)
    .maybeSingle<ChartRow>();

  if (error) throw new Error(error.message);
  return data ? rowToChart(data) : null;
}

/**
 * Make `birth` the account's primary chart, and return the row it lives in.
 *
 * Idempotent: pushing details the account already holds writes nothing and
 * returns the existing row, so a sync on every launch does not accumulate
 * duplicates of the same chart.
 */
export async function pushPrimaryChart(
  userId: string,
  birth: BirthDetails,
): Promise<string | null> {
  if (!supabase) return null;

  const existing = await fetchPrimaryChart(userId);
  if (existing && sameChart(existing.birth, birth)) return existing.id;

  // Insert as non-primary first to avoid uniqueness constraint on `is_primary = true`
  const { data, error } = await supabase
    .from('charts')
    .insert({
      user_id: userId,
      birth_date: birth.date,
      birth_time: birth.time,
      latitude: birth.latitude,
      longitude: birth.longitude,
      place: birth.place ?? null,
      timezone: birth.timezone ?? null,
      is_primary: false,
    })
    .select('id')
    .single<{ id: string }>();

  if (error) throw new Error(error.message);

  // Atomically swap the new chart to primary
  const { error: rpcError } = await supabase.rpc('set_primary_chart', { new_chart_id: data.id });
  if (rpcError) throw new Error(rpcError.message);

  return data.id;
}

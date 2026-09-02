/**
 * The device as a cache.
 *
 * Shared by the course and by the reading, which cache for different reasons
 * that happen to want the same machinery. Chapters are cached to make the app
 * small and work on a train. A reading is cached because generating one costs
 * a request against a quota of **20 per model per day** — so on the device is
 * where caching actually protects a person's ability to use the app, in a way
 * a server-side cache cannot: it survives cold starts, redeploys and a backend
 * that spun down overnight.
 *
 * Everything is namespaced under `enumasky.` so a whole family can be dropped at
 * once when the chart it was computed for changes.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

import type { BirthDetails } from './types';

/** Chapters and the course index. */
export const COURSE_NAMESPACE = 'enumasky.course.';

/** Generated readings. */
export const READING_NAMESPACE = 'enumasky.reading.';

/** The home screen's daily line. */
export const TIP_NAMESPACE = 'enumasky.tip.';

/**
 * The one line the home screen borrows from the chart.
 *
 * The lagna is arithmetic the backend already returns, but the home screen is
 * the first thing a launch paints and it must not wait on a request to say
 * something true. Kept here so the second launch onward reads it from disk, and
 * so it works on a train.
 */
export const HOME_NAMESPACE = 'enumasky.home.';

/**
 * The current spread and whatever reading was paid for on it.
 *
 * Not cleared with the chart caches below: a tarot draw is not computed from
 * the birth details and does not go stale when they change. It is the one thing
 * the app keeps that belongs to the moment rather than to the nativity.
 */
export const TAROT_NAMESPACE = 'enumasky.tarot.';

/**
 * Enough of the birth details to notice a different chart, and nothing more.
 *
 * Three decimal places is about a hundred metres — far finer than anything that
 * moves a cusp, and coarse enough that a re-selected city cannot miss its own
 * cached entries on a float's last digit.
 */
export function birthKey(birth: BirthDetails | null): string {
  if (!birth) return 'none';
  return `${birth.date}T${birth.time}@${birth.latitude.toFixed(3)},${birth.longitude.toFixed(3)}`;
}

export async function readCache<T>(key: string): Promise<T | null> {
  try {
    const raw = await AsyncStorage.getItem(key);
    return raw ? (JSON.parse(raw) as T) : null;
  } catch {
    return null;
  }
}

export async function writeCache(key: string, value: unknown): Promise<void> {
  try {
    await AsyncStorage.setItem(key, JSON.stringify(value));
  } catch {
    // A full disk should not stop someone reading; the network copy still works.
  }
}

/** Drop every key under a prefix. */
export async function clearNamespace(prefix: string): Promise<void> {
  const keys = await AsyncStorage.getAllKeys();
  const ours = keys.filter((key) => key.startsWith(prefix));
  if (ours.length) await AsyncStorage.multiRemove(ours);
}

/** Drop every key under `prefix` except `keep`. */
export async function pruneNamespace(prefix: string, keep: string): Promise<void> {
  const keys = await AsyncStorage.getAllKeys();
  const stale = keys.filter((key) => key.startsWith(prefix) && key !== keep);
  if (stale.length) await AsyncStorage.multiRemove(stale);
}

/**
 * Everything computed from the birth details.
 *
 * Both caches key on the chart, so a new chart cannot be answered from either —
 * but the old entries would sit there unreachable forever, and a chapter's
 * "in your chart" line belongs to a chart the reader has left behind.
 */
export async function clearChartCaches(): Promise<void> {
  await Promise.all([
    clearNamespace(COURSE_NAMESPACE),
    clearNamespace(READING_NAMESPACE),
    clearNamespace(TIP_NAMESPACE),
    clearNamespace(HOME_NAMESPACE),
  ]);
}

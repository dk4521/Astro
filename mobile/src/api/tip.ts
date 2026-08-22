/**
 * The home screen's daily line, with the device as a cache.
 *
 * This is the most expensive thing the app does, measured the way that matters:
 * not per call, but per launch. It is the first thing on the first screen, and
 * a model request costs one of **twenty a day** on the free tier. Without this
 * cache, opening the app three times in a morning would spend a seventh of the
 * day's capacity re-reading one sentence.
 *
 * The key is the chart, the language, the companion, and the date — and the
 * date is the whole invalidation policy. The backend builds the tip's brief
 * with `as of:` at day precision, so a tip is about *this day's* running
 * period; keeping it for the day is correct rather than merely thrifty, and
 * dropping it at the boundary is what stops yesterday's line greeting someone
 * tomorrow. UTC, to match the boundary the backend actually uses.
 *
 * The companion is in the key because the line is written in their voice.
 * Switching from Priya to Kabir has to produce a new line, or Kabir opens by
 * saying something in Priya's words.
 *
 * A line that failed grounding is never kept. A tip is told to name no
 * placements at all, so a contradiction means the model reached for one anyway
 * — and storing that would hand the same reader the same slip all day.
 */

import { TIP_NAMESPACE, birthKey, pruneNamespace, readCache, writeCache } from './cache';
import { fetchTip } from './client';
import type { BirthDetails, Language, Tip } from './types';

/** The backend's own day boundary — `as of: %Y-%m-%d` on a UTC moment. */
function utcDay(): string {
  return new Date().toISOString().slice(0, 10);
}

function familyKey(birth: BirthDetails, language: Language, companion: string): string {
  return `${TIP_NAMESPACE}${birthKey(birth)}.${language}.${companion || 'none'}.`;
}

export async function loadTip(
  birth: BirthDetails,
  language: Language,
  companion: string | null,
): Promise<Tip> {
  const family = familyKey(birth, language, companion ?? '');
  const key = `${family}${utcDay()}.v1`;

  const cached = await readCache<Tip>(key);
  if (cached) return cached;

  const tip = await fetchTip(birth, language, companion);
  if (tip.grounded) {
    await writeCache(key, tip);
    // Yesterday's line for this same reader is unreachable now — the key it
    // sits under can never be asked for again.
    await pruneNamespace(family, key);
  }
  return tip;
}

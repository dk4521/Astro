/**
 * The opening reading, with the device as a cache.
 *
 * This is the one screen in the app that costs money to open. A reading is a
 * model call, and the free tier allows **20 per model per day** — a limit our
 * own testing exhausted in a single evening. Without a cache here, one person
 * opening the app four times, or switching language twice, would spend a
 * meaningful share of the day's capacity on text they have already read.
 *
 * The key carries the date, and that is the whole invalidation policy. The
 * backend builds its fact brief with `as of:` at day precision, so a reading is
 * an explanation of *this day's* running dasha; keeping it for the day is
 * correct rather than merely thrifty, and dropping it at the day boundary is
 * what stops a stale period being explained tomorrow. UTC, to match the
 * boundary the backend actually uses rather than one near it.
 *
 * A reading that failed grounding is never kept. Storing it would take the
 * product's one visible failure — text that contradicts the computed chart —
 * and hand the same reader the same wrong reading every time they opened the
 * screen, for a day. The retry costs a request they were going to spend anyway.
 */

import { READING_NAMESPACE, birthKey, pruneNamespace, readCache, writeCache } from './cache';
import { fetchInterpretation } from './client';
import type { BirthDetails, Interpretation, Language } from './types';

/** The backend's own day boundary — `as of: %Y-%m-%d` on a UTC moment. */
function utcDay(): string {
  return new Date().toISOString().slice(0, 10);
}

function familyKey(birth: BirthDetails, language: Language): string {
  return `${READING_NAMESPACE}${birthKey(birth)}.${language}.`;
}

export async function loadInterpretation(
  birth: BirthDetails,
  language: Language,
): Promise<Interpretation> {
  const key = `${familyKey(birth, language)}${utcDay()}.v1`;

  const cached = await readCache<Interpretation>(key);
  if (cached) return cached;

  const interpretation = await fetchInterpretation(birth, language);

  if (interpretation.grounded) {
    await writeCache(key, interpretation);
    // Yesterday's reading for this chart and language is now unreachable — the
    // key it lives under can never be asked for again. Pruning on write keeps
    // the store to one entry per chart per language rather than one per day
    // since the app was installed.
    await pruneNamespace(familyKey(birth, language), key);
  }

  return interpretation;
}

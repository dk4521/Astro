/**
 * Local persistence of the user's birth details.
 *
 * Birth data is the one thing the app must never make the user re-enter, and
 * it is also personal — so it stays on the device until there is a real account
 * system to attach it to.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

import type { BirthDetails } from './types';

const KEY = 'kosmiq.birthDetails.v1';

export async function saveBirthDetails(details: BirthDetails): Promise<void> {
  await AsyncStorage.setItem(KEY, JSON.stringify(details));
}

export async function loadBirthDetails(): Promise<BirthDetails | null> {
  const raw = await AsyncStorage.getItem(KEY);
  if (!raw) return null;

  try {
    const parsed = JSON.parse(raw) as BirthDetails;
    // Guard against a stored shape from an older build.
    if (
      typeof parsed?.date === 'string' &&
      typeof parsed?.time === 'string' &&
      typeof parsed?.latitude === 'number' &&
      typeof parsed?.longitude === 'number'
    ) {
      return parsed;
    }
    return null;
  } catch {
    return null;
  }
}

export async function clearBirthDetails(): Promise<void> {
  await AsyncStorage.removeItem(KEY);
}

// --- Course progress -------------------------------------------------------
//
// Chapters read, by slug. Kept next to the birth details and for the same
// reason: this is the user's own record of what they have worked through, and
// losing it to a reinstall would be worse than trivial. It moves to Supabase
// when accounts exist.

const PROGRESS_KEY = 'kosmiq.learn.progress.v1';

export async function loadProgress(): Promise<string[]> {
  const raw = await AsyncStorage.getItem(PROGRESS_KEY);
  if (!raw) return [];

  try {
    const parsed = JSON.parse(raw);
    return Array.isArray(parsed) ? parsed.filter((s): s is string => typeof s === 'string') : [];
  } catch {
    return [];
  }
}

/** Idempotent: marking a chapter read twice is not an error. */
export async function markChapterRead(slug: string): Promise<string[]> {
  const current = await loadProgress();
  if (current.includes(slug)) return current;

  const next = [...current, slug];
  await AsyncStorage.setItem(PROGRESS_KEY, JSON.stringify(next));
  return next;
}

export async function clearProgress(): Promise<void> {
  await AsyncStorage.removeItem(PROGRESS_KEY);
}

// --- Accounts --------------------------------------------------------------

const SEEN_ACCOUNTS_KEY = 'kosmiq.seenAccounts.v1';

/**
 * Whether the account screen has been shown once.
 *
 * Signing in is optional, so someone who chose to continue without an account
 * must not be asked again every launch — that is a nag, not an offer.
 */
export async function hasSeenAccounts(): Promise<boolean> {
  return (await AsyncStorage.getItem(SEEN_ACCOUNTS_KEY)) === 'yes';
}

export async function markAccountsSeen(): Promise<void> {
  await AsyncStorage.setItem(SEEN_ACCOUNTS_KEY, 'yes');
}

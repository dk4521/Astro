/**
 * Local persistence of the user's birth details.
 *
 * Birth data is the one thing the app must never make the user re-enter, and it
 * is also personal — so the device stays the source of truth. An account
 * mirrors it (see `src/sync/`), it does not take over from it: everything here
 * keeps working signed out, offline, and in a build with no Supabase project
 * configured at all.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

import type { BirthDetails } from './types';

const KEY = 'kosmiq.birthDetails.v1';

/**
 * When the details below were last written, as epoch milliseconds.
 *
 * Kept beside the record rather than inside it because `BirthDetails` is a wire
 * type — it goes to the API on every chart request, and a field the backend has
 * no use for does not belong in that payload.
 *
 * It exists for one job: deciding which copy wins when a phone and an account
 * disagree. Two devices editing the same birth time is rare but not impossible,
 * and "whichever device signed in last" is the wrong answer to that.
 */
const SAVED_AT_KEY = 'kosmiq.birthDetails.savedAt.v1';

export async function saveBirthDetails(details: BirthDetails): Promise<void> {
  await AsyncStorage.multiSet([
    [KEY, JSON.stringify(details)],
    [SAVED_AT_KEY, String(Date.now())],
  ]);
}

/** Epoch ms of the last local write, or null if nothing has been saved. */
export async function birthDetailsSavedAt(): Promise<number | null> {
  const raw = await AsyncStorage.getItem(SAVED_AT_KEY);
  if (!raw) return null;
  const value = Number(raw);
  return Number.isFinite(value) ? value : null;
}

/**
 * Write details that came from the account rather than from this device.
 *
 * Separate from `saveBirthDetails` so the stamp carries the *remote* write time.
 * Stamping a pulled copy with `Date.now()` would make it look like the newest
 * edit anywhere and let a stale account copy beat a real edit on another phone.
 */
export async function saveBirthDetailsFromRemote(
  details: BirthDetails,
  savedAt: number,
): Promise<void> {
  await AsyncStorage.multiSet([
    [KEY, JSON.stringify(details)],
    [SAVED_AT_KEY, String(savedAt)],
  ]);
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
  await AsyncStorage.multiRemove([KEY, SAVED_AT_KEY]);
}

// --- Course progress -------------------------------------------------------
//
// Chapters read, by slug. Kept next to the birth details and for the same
// reason: this is the user's own record of what they have worked through, and
// losing it to a reinstall would be worse than trivial. With an account it is
// mirrored to Supabase and merged as a union, so two devices reading different
// chapters add up instead of overwriting each other.

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

/** Overwrite the whole set. Used by the sync merge, which computes a union. */
export async function replaceProgress(slugs: string[]): Promise<void> {
  await AsyncStorage.setItem(PROGRESS_KEY, JSON.stringify(slugs));
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

// --- Remote row ids --------------------------------------------------------
//
// Which rows in the account this device is mirroring into. Cached so an ordinary
// launch does not re-query for them, and cleared on sign-out because they belong
// to the account that was signed in, not to the phone.
//
// The conversation hangs off the chart: change your birth details and the old
// conversation stays with the old chart rather than following the new one into a
// reading it was never about.

const IDS_KEY = 'kosmiq.sync.ids.v1';

export type SyncIds = {
  chartId: string | null;
  conversationId: string | null;
};

const NO_IDS: SyncIds = { chartId: null, conversationId: null };

export async function loadSyncIds(): Promise<SyncIds> {
  const raw = await AsyncStorage.getItem(IDS_KEY);
  if (!raw) return NO_IDS;

  try {
    const parsed = JSON.parse(raw) as Partial<SyncIds>;
    return {
      chartId: typeof parsed?.chartId === 'string' ? parsed.chartId : null,
      conversationId: typeof parsed?.conversationId === 'string' ? parsed.conversationId : null,
    };
  } catch {
    return NO_IDS;
  }
}

/** Remember the chart row. A different chart drops the conversation with it. */
export async function rememberChartId(chartId: string | null): Promise<SyncIds> {
  const current = await loadSyncIds();
  const next: SyncIds = {
    chartId,
    conversationId: current.chartId === chartId ? current.conversationId : null,
  };
  await AsyncStorage.setItem(IDS_KEY, JSON.stringify(next));
  return next;
}

export async function rememberConversationId(conversationId: string | null): Promise<void> {
  const current = await loadSyncIds();
  await AsyncStorage.setItem(IDS_KEY, JSON.stringify({ ...current, conversationId }));
}

export async function clearSyncIds(): Promise<void> {
  await AsyncStorage.removeItem(IDS_KEY);
}

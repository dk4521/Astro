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

const KEY = 'enumasky.birthDetails.v1';

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
const SAVED_AT_KEY = 'enumasky.birthDetails.savedAt.v1';

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

const PROGRESS_KEY = 'enumasky.learn.progress.v1';

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

const SEEN_ACCOUNTS_KEY = 'enumasky.seenAccounts.v1';

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

// --- Name -------------------------------------------------------------------

const NAME_KEY = 'enumasky.name.v1';

/**
 * What to call the reader. Empty until they say.
 *
 * Optional, and stays optional: the home screen greets by name when it has one
 * and simply doesn't when it doesn't. Nothing computed depends on it — a name
 * is not birth data — so it never blocks a screen the way missing birth details
 * do.
 */
export async function loadName(): Promise<string> {
  return (await AsyncStorage.getItem(NAME_KEY)) ?? '';
}

export async function saveName(name: string): Promise<void> {
  const trimmed = name.trim();
  if (trimmed) await AsyncStorage.setItem(NAME_KEY, trimmed);
  else await AsyncStorage.removeItem(NAME_KEY);
}

// --- Chat companion --------------------------------------------------------

const PERSONA_KEY = 'enumasky.persona.v1';

/** Who the chat is with. Null until someone has been picked. */
export async function loadPersona(): Promise<string | null> {
  return AsyncStorage.getItem(PERSONA_KEY);
}

export async function savePersona(id: string): Promise<void> {
  await AsyncStorage.setItem(PERSONA_KEY, id);
}

// --- Display language -------------------------------------------------------

const LANGUAGE_KEY = 'enumasky.displayLanguage.v1';

/**
 * Hindi or English for the screens that show computed values.
 *
 * Stored rather than held per screen: someone who picks Hindi on the chart has
 * said what they read in, and having to say it again on the next screen is the
 * app forgetting them. Defaults to English until they choose.
 */
export async function loadDisplayLanguage(): Promise<'en' | 'hi'> {
  return (await AsyncStorage.getItem(LANGUAGE_KEY)) === 'hi' ? 'hi' : 'en';
}

export async function saveDisplayLanguage(language: 'en' | 'hi'): Promise<void> {
  await AsyncStorage.setItem(LANGUAGE_KEY, language);
}

// --- Deleting everything ----------------------------------------------------

/**
 * Every key this app has ever written on this phone.
 *
 * For one caller: deleting the account. Signing out deliberately leaves the
 * birth details behind — it is not a request to be forgotten, and typing a
 * birth time back in is the last thing someone signing out expects. Deleting
 * the account is that request, and leaving the mirror of a deleted account
 * sitting on the phone would make the promise a half-truth.
 *
 * By prefix rather than `AsyncStorage.clear()`, which would also take anything
 * a library keeps beside us — the Supabase session on web, where there is no
 * keychain to hold it, is exactly that.
 */
export async function clearDeviceData(): Promise<void> {
  const keys = await AsyncStorage.getAllKeys();
  // The one prefix every key above shares; `api/cache.ts` names the cache
  // families under it, and `api/migrate.ts` is why it is not `kosmiq.` any more.
  const ours = keys.filter((key) => key.startsWith('enumasky.'));
  if (ours.length > 0) await AsyncStorage.multiRemove(ours);
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

const IDS_KEY = 'enumasky.sync.ids.v1';

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

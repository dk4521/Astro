/**
 * Everything the app stored under its old name.
 *
 * The app was called Kosmiq, and every key it wrote on the device began with
 * `kosmiq.`. Renaming it to Enuma Sky renamed the keys with it — which is
 * correct, and on its own would have quietly emptied the app for anyone already
 * carrying a build: birth details, name, companion, language, course progress
 * and the sync row ids all still sit on the phone, under names nothing reads
 * any more. `clearNamespace` would not even collect them, because it only
 * scans the new prefix.
 *
 * So they are moved once, on the first launch of a renamed build, and the
 * originals are deleted. Nothing is merged and nothing is parsed: a value is
 * bytes under one name being written under another, so a key this file has
 * never heard of travels with the rest and a shape change is not its business.
 *
 * **This file is temporary.** Once no device can still be carrying a Kosmiq
 * build — the app had not been released, so that is a short list — delete it
 * and its call in `app/_layout.tsx`. It is deliberately standalone so that
 * deletion is one file and one line.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';

/** What every key used to start with. */
const LEGACY = 'kosmiq.';

/** What every key starts with now — `api/cache.ts` and `api/storage.ts`. */
const CURRENT = 'enumasky.';

/**
 * Move the old keys to the new names. Safe to call on every launch.
 *
 * Never throws. A phone that cannot complete this is a phone whose reader
 * types their birth details again — the same as any fresh install — and that
 * is a far better outcome than an app that will not open.
 */
export async function migrateLegacyKeys(): Promise<void> {
  try {
    const keys = await AsyncStorage.getAllKeys();
    const legacy = keys.filter((key) => key.startsWith(LEGACY));
    if (legacy.length === 0) return;

    const existing = new Set(keys);
    const entries = await AsyncStorage.multiGet(legacy);

    const moves: [string, string][] = [];
    for (const [key, value] of entries) {
      if (value === null) continue;
      const renamed = `${CURRENT}${key.slice(LEGACY.length)}`;
      // Never overwrite a key the new build has already written. If both exist,
      // the current one is the one someone has used since — the old copy is a
      // fossil, not an edit.
      if (!existing.has(renamed)) moves.push([renamed, value]);
    }

    if (moves.length > 0) await AsyncStorage.multiSet(moves);

    // Dropped whether or not they moved. One that did not move was already
    // superseded, and leaving any of them means doing all of this again on
    // every launch for the life of the install.
    await AsyncStorage.multiRemove(legacy);
  } catch {
    // Deliberately silent: see above.
  }
}

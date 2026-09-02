/**
 * Where the Supabase session actually lives.
 *
 * It used to live in `AsyncStorage`, which on both platforms is a plain file in
 * the app's sandbox: on Android an unencrypted SQLite database, on iOS a JSON
 * file. That is the right place for a birth chart and the wrong place for a
 * refresh token, which is a long-lived credential that can mint access tokens
 * until it is revoked. Anyone with the file has the account — a rooted or
 * jailbroken phone, an `adb backup` on a device that allows it, a forensic
 * image, a shared laptop with an emulator snapshot on it.
 *
 * `expo-secure-store` puts it in the Android Keystore and the iOS Keychain
 * instead, where the key material is held by the OS and, on a modern device,
 * backed by hardware. It is not proof against a determined attacker with the
 * unlocked phone in their hand. It is proof against every case above.
 *
 * **Why the chunking.** SecureStore is meant for small values — Android warns
 * above 2048 bytes and can refuse outright — and a Supabase session is not
 * small: two JWTs plus the user object runs to several kilobytes. So a value is
 * split across numbered keys and a header records how many there are. The
 * header is written *last* on the way in and read first on the way out, which
 * is what makes a write interrupted halfway read back as absent rather than as
 * a truncated session that fails in a way nobody can debug.
 *
 * **Why the migration.** A signed-in user upgrading to this build has their
 * session in the old place. Reading through to AsyncStorage once, moving it,
 * and deleting the original means they stay signed in; without it, every
 * existing user is silently logged out by a release that was supposed to be
 * about security. It runs once per key and leaves nothing behind.
 *
 * **Web is not covered**, and cannot be: there is no keychain in a browser, and
 * `expo-secure-store` has no web implementation. The adapter falls back to
 * AsyncStorage there, which is `localStorage` — exactly what a Supabase web app
 * uses anyway. The phone is what this is for.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import * as SecureStore from 'expo-secure-store';
import { Platform } from 'react-native';

/** Comfortably inside Android's limit, with room for the key name itself. */
const CHUNK = 1800;

/** How many pieces one value was split into. Written last, read first. */
const header = (key: string) => `${key}.parts`;
const part = (key: string, index: number) => `${key}.${index}`;

const OPTIONS: SecureStore.SecureStoreOptions = {
  // The default is `WHEN_UNLOCKED`, which is already right: a background token
  // refresh needs the value while the phone sits locked in a pocket, and
  // `WHEN_UNLOCKED_THIS_DEVICE_ONLY` would additionally keep it out of an
  // iCloud Keychain restore — which sounds stricter and would silently sign
  // people out when they move to a new phone. Named rather than left implicit,
  // because the difference is worth having thought about.
  keychainAccessible: SecureStore.WHEN_UNLOCKED,
};

/** True on web, where there is no keychain to use. */
const UNAVAILABLE = Platform.OS === 'web';

async function readAll(key: string): Promise<string | null> {
  const count = await SecureStore.getItemAsync(header(key), OPTIONS);
  if (count === null) return null;

  const parts = Number(count);
  if (!Number.isInteger(parts) || parts < 1) return null;

  const pieces: string[] = [];
  for (let index = 0; index < parts; index += 1) {
    const piece = await SecureStore.getItemAsync(part(key, index), OPTIONS);
    // A missing piece means a write that did not finish or a store that was
    // partly cleared. Half a session is worse than none — it would be handed to
    // Supabase as a valid-looking string and fail somewhere far from here.
    if (piece === null) return null;
    pieces.push(piece);
  }

  return pieces.join('');
}

async function removeAll(key: string): Promise<void> {
  const count = await SecureStore.getItemAsync(header(key), OPTIONS);

  // The header goes first: after this the value is gone as far as any reader is
  // concerned, whatever happens to the rest.
  await SecureStore.deleteItemAsync(header(key), OPTIONS);

  const parts = Number(count ?? 0);
  if (!Number.isInteger(parts) || parts < 1) return;

  for (let index = 0; index < parts; index += 1) {
    await SecureStore.deleteItemAsync(part(key, index), OPTIONS);
  }
}

async function writeAll(key: string, value: string): Promise<void> {
  // Old pieces first, or a shorter value would leave the tail of a longer one
  // behind and `readAll` would splice the two together.
  await removeAll(key);

  const pieces: string[] = [];
  for (let at = 0; at < value.length; at += CHUNK) {
    pieces.push(value.slice(at, at + CHUNK));
  }

  for (let index = 0; index < pieces.length; index += 1) {
    await SecureStore.setItemAsync(part(key, index), pieces[index], OPTIONS);
  }

  // Last, so an interrupted write is invisible rather than corrupt.
  await SecureStore.setItemAsync(header(key), String(pieces.length), OPTIONS);
}

/**
 * Move a session written by an older build, once.
 *
 * Failure here is not worth propagating: the worst case is that somebody has to
 * sign in again, which is exactly what happens if this throws and takes the
 * read with it.
 */
async function migrateFromAsyncStorage(key: string): Promise<string | null> {
  try {
    const legacy = await AsyncStorage.getItem(key);
    if (legacy === null) return null;

    await writeAll(key, legacy);
    await AsyncStorage.removeItem(key);
    return legacy;
  } catch {
    return null;
  }
}

/**
 * The storage adapter handed to `createClient`.
 *
 * Every method swallows its errors and answers null, because that is the
 * contract Supabase's client is written against — a throw from here surfaces
 * inside `getSession()` and takes down whichever screen asked. Losing a session
 * is recoverable by signing in; a screen that cannot render is not.
 */
export const SecureSessionStore = {
  async getItem(key: string): Promise<string | null> {
    if (UNAVAILABLE) return AsyncStorage.getItem(key);

    try {
      const stored = await readAll(key);
      if (stored !== null) return stored;
      return await migrateFromAsyncStorage(key);
    } catch {
      return null;
    }
  },

  async setItem(key: string, value: string): Promise<void> {
    if (UNAVAILABLE) return AsyncStorage.setItem(key, value);

    try {
      await writeAll(key, value);
    } catch {
      // Nothing useful to do. The session stays in memory for this launch and
      // the person signs in again next time — which is the failure this whole
      // file is willing to accept in exchange for the token not sitting in a
      // readable file.
    }
  },

  async removeItem(key: string): Promise<void> {
    if (UNAVAILABLE) return AsyncStorage.removeItem(key);

    try {
      await removeAll(key);
    } catch {
      // Ignored for the same reason, with one addition: sign-out also clears
      // the client's in-memory session, so a failure here does not leave
      // anybody looking signed in.
    }

    // Belt and braces for a phone that upgraded mid-session and still has the
    // old copy: signing out must not leave a readable token behind.
    try {
      await AsyncStorage.removeItem(key);
    } catch {
      // Already gone, or never there.
    }
  },
};

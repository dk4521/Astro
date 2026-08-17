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

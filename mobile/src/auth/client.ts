/**
 * The Supabase client.
 *
 * Optional on purpose. Until a project is configured the app runs exactly as it
 * did before — birth details and course progress on the device, no account —
 * because an app that refuses to open without a backend nobody has set up yet
 * is worse than one that quietly works offline. `isConfigured()` is what every
 * caller checks.
 *
 * Two Expo details worth knowing, both verified against SDK 57 rather than
 * copied from the standard React Native guide:
 *
 * - **No `react-native-url-polyfill`.** Expo's winter runtime installs `URL`
 *   and `URLSearchParams` globally, which is the only reason that polyfill is
 *   usually needed.
 * - **Auto-refresh has to follow the app's lifecycle.** A background timer
 *   refreshing a token is wasted work and, on Android, gets throttled anyway —
 *   so refresh is started and stopped with the foreground state.
 */

import AsyncStorage from '@react-native-async-storage/async-storage';
import { createClient, type SupabaseClient } from '@supabase/supabase-js';
import Constants from 'expo-constants';
import { AppState } from 'react-native';

type Extra = { supabaseUrl?: string; supabaseAnonKey?: string };

function setting(envValue: string | undefined, key: keyof Extra): string | null {
  const fromEnv = envValue?.trim();
  if (fromEnv) return fromEnv;

  const extra = Constants.expoConfig?.extra as Extra | undefined;
  const fromExtra = extra?.[key]?.trim();
  return fromExtra || null;
}

const URL_VALUE = setting(process.env.EXPO_PUBLIC_SUPABASE_URL, 'supabaseUrl');
const ANON_KEY = setting(process.env.EXPO_PUBLIC_SUPABASE_ANON_KEY, 'supabaseAnonKey');

/** Whether accounts are available in this build at all. */
export function isConfigured(): boolean {
  return Boolean(URL_VALUE && ANON_KEY);
}

export const supabase: SupabaseClient | null =
  URL_VALUE && ANON_KEY
    ? createClient(URL_VALUE, ANON_KEY, {
        auth: {
          storage: AsyncStorage,
          autoRefreshToken: true,
          persistSession: true,
          // There is no URL bar to read a session out of on a phone, and
          // leaving this on makes the client wait for one that never arrives.
          detectSessionInUrl: false,
        },
      })
    : null;

if (supabase) {
  AppState.addEventListener('change', (state) => {
    if (state === 'active') supabase.auth.startAutoRefresh();
    else supabase.auth.stopAutoRefresh();
  });
}

/**
 * Turn Supabase's error text into something worth showing a person.
 *
 * Its messages are written for developers; two of them are things a user can
 * actually act on, and the rest are noise at the bottom of a form.
 */
export function authErrorMessage(error: { message?: string } | null): string {
  const raw = error?.message ?? '';

  if (/invalid login credentials/i.test(raw)) {
    return 'That email and password do not match an account.';
  }
  if (/email not confirmed/i.test(raw)) {
    return 'Check your inbox and confirm your email, then sign in.';
  }
  if (/user already registered|already been registered/i.test(raw)) {
    return 'An account with that email already exists. Sign in instead.';
  }
  if (/password should be at least/i.test(raw)) {
    return 'Use a password of at least six characters.';
  }
  if (/network|fetch/i.test(raw)) {
    return 'Could not reach Supabase. Check your connection.';
  }
  return raw || 'Something went wrong. Try again.';
}

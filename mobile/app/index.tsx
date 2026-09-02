/**
 * Entry route: decide where the user belongs before showing anything.
 *
 * Four questions in order — is the session loaded, has the account finished
 * syncing, do we have birth details, has this person seen the account screen —
 * and no screen renders until all four have a definite answer. Showing
 * onboarding for even a frame to someone who already filled it in makes the app
 * feel like it forgot them, and the same is true of a sign-in screen shown to
 * someone already signed in.
 *
 * The sync wait is what makes a new phone work: a signed-in user's birth details
 * arrive from their account a moment after the session does, and reading local
 * storage before that lands would send them straight to onboarding to type in a
 * birth time the app already knows.
 *
 * Signing in is never required. The account screen appears once, and
 * "Continue without an account" is a real answer that is remembered.
 */

import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { useAuth } from '../src/auth/context';
import { useSync } from '../src/sync/context';
import { hasSeenAccounts, loadBirthDetails } from '../src/api/storage';
import { colors } from '../src/theme';

type Target = '/onboarding' | '/home' | '/sign-in';

export default function Index() {
  const { ready, session, available } = useAuth();
  const { ready: synced } = useSync();
  const [target, setTarget] = useState<Target | null>(null);

  useEffect(() => {
    if (!ready || !synced) return;

    let cancelled = false;
    (async () => {
      const [birth, seenAccounts] = await Promise.all([
        loadBirthDetails(),
        hasSeenAccounts(),
      ]);
      if (cancelled) return;

      // Offer the account screen once, and only when there is something behind
      // it. Someone who declined is not asked again on every launch.
      if (available && !session && !seenAccounts) {
        setTarget('/sign-in');
        return;
      }
      setTarget(birth ? '/home' : '/onboarding');
    })();

    return () => {
      cancelled = true;
    };
  }, [ready, synced, session, available]);

  if (!target) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.accent} />
      </View>
    );
  }

  return <Redirect href={target} />;
}

const styles = StyleSheet.create({
  loading: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

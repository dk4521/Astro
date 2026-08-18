/**
 * Entry route: decide where the user belongs before showing anything.
 *
 * Three questions in order — is the session loaded, do we have birth details,
 * has this person seen the account screen — and no screen renders until all
 * three have a definite answer. Showing onboarding for even a frame to someone
 * who already filled it in makes the app feel like it forgot them, and the same
 * is true of a sign-in screen shown to someone already signed in.
 *
 * Signing in is never required. The account screen appears once, and
 * "Continue without an account" is a real answer that is remembered.
 */

import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { useAuth } from '../src/auth/context';
import { hasSeenAccounts, loadBirthDetails } from '../src/api/storage';
import { colors } from '../src/theme';

type Target = '/onboarding' | '/chart' | '/sign-in';

export default function Index() {
  const { ready, session, available } = useAuth();
  const [target, setTarget] = useState<Target | null>(null);

  useEffect(() => {
    if (!ready) return;

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
      setTarget(birth ? '/chart' : '/onboarding');
    })();

    return () => {
      cancelled = true;
    };
  }, [ready, session, available]);

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
    backgroundColor: colors.bg,
  },
});

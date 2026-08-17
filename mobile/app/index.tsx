/**
 * Entry route: decide where the user belongs before showing anything.
 *
 * Returning users go straight to their chart. Showing the onboarding form for
 * even a frame to someone who has already filled it in makes the app feel like
 * it forgot them.
 */

import { Redirect } from 'expo-router';
import { useEffect, useState } from 'react';
import { ActivityIndicator, StyleSheet, View } from 'react-native';

import { loadBirthDetails } from '../src/api/storage';
import { colors } from '../src/theme';

export default function Index() {
  const [target, setTarget] = useState<'/onboarding' | '/chart' | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadBirthDetails().then((saved) => {
      if (!cancelled) setTarget(saved ? '/chart' : '/onboarding');
    });
    return () => {
      cancelled = true;
    };
  }, []);

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

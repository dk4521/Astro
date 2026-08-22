/**
 * Kundali Milan.
 *
 * Its own screen rather than a section at the foot of the chart, which is where
 * it started: below the panchang and the provenance card it took five scrolls to
 * reach, and a feature nobody scrolls to is a feature nobody has.
 *
 * The screen is a frame and nothing more — `Matching` holds the form, the
 * request and the table. What lives here is what every drawer screen needs: the
 * bar, the language, and the birth details the whole thing hangs off.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, ScrollView, StyleSheet, View } from 'react-native';

import {
  loadBirthDetails,
  loadDisplayLanguage,
  saveDisplayLanguage,
} from '../../src/api/storage';
import type { BirthDetails } from '../../src/api/types';
import { strings, type DisplayLanguage } from '../../src/i18n';
import { LanguagePicker } from '../../src/components/LanguagePicker';
import { Matching } from '../../src/components/Matching';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { colors, space } from '../../src/theme';

export default function MatchingScreen() {
  const router = useRouter();
  const [birth, setBirth] = useState<BirthDetails | null>(null);
  const [language, setLanguage] = useState<DisplayLanguage | undefined>(undefined);

  useEffect(() => {
    loadDisplayLanguage().then(setLanguage);
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const saved = await loadBirthDetails();
      if (cancelled) return;
      // Milan needs a nakshatra on both sides, and one of them is the reader's.
      if (!saved) router.replace('/onboarding');
      else setBirth(saved);
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const t = strings(language ?? 'en');

  return (
    <View style={styles.flex}>
      <ScreenHeader
        title={t.matching}
        right={
          language ? <LanguagePicker value={language} onChange={chooseLanguage} /> : null
        }
      />

      {birth && language ? (
        <ScrollView
          contentContainerStyle={styles.content}
          keyboardShouldPersistTaps="handled"
        >
          <Matching birth={birth} language={language} />
        </ScrollView>
      ) : (
        <View style={styles.loading}>
          <ActivityIndicator color={colors.accent} />
        </View>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, paddingBottom: space.xxl },
  loading: { flex: 1, alignItems: 'center', justifyContent: 'center' },
});

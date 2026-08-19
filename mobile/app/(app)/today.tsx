/**
 * Today.
 *
 * The screen a user can open several times a day, which is exactly why it does
 * not touch the model: panchang for this moment and the active dasha are both
 * arithmetic. No quota, no cost, no waiting — and nothing here can be wrong in
 * the way generated text can be wrong.
 *
 * It deliberately does not offer a "daily prediction". The tradition's honest
 * daily layer is the panchang, and that is what this shows.
 */

import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import { fetchToday } from '../../src/api/client';
import { loadBirthDetails } from '../../src/api/storage';
import type { Today as TodayData } from '../../src/api/types';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, ErrorNote, Label, Row } from '../../src/components/ui';
import { colors, space, type } from '../../src/theme';

const LEVELS = ['Mahadasha', 'Antardasha', 'Pratyantardasha'];

function formatDate(iso: string): string {
  return new Date(iso).toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

export default function Today() {
  const [data, setData] = useState<TodayData | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async () => {
    try {
      const birth = await loadBirthDetails();
      if (!birth) return;
      setData(await fetchToday(birth));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not reach the server');
    } finally {
      setLoading(false);
    }
  }, []);

  // Refetched on focus: a tithi can turn while the app sits in the background.
  useFocusEffect(
    useCallback(() => {
      load();
    }, [load]),
  );

  const refresh = useCallback(async () => {
    setRefreshing(true);
    await load();
    setRefreshing(false);
  }, [load]);

  const today = new Date().toLocaleDateString(undefined, {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  return (
    <View style={styles.flex}>
      <ScreenHeader title="Today" />

      <ScrollView
        contentContainerStyle={styles.content}
        refreshControl={
          <RefreshControl refreshing={refreshing} onRefresh={refresh} tintColor={colors.accent} />
        }
      >
        {loading && !data ? (
          <View style={styles.loading}>
            <ActivityIndicator color={colors.accent} />
          </View>
        ) : null}

        {error && !data ? (
          <View>
            <ErrorNote message={error} />
            <View style={styles.retry}>
              <Button title="Try again" onPress={refresh} variant="ghost" />
            </View>
          </View>
        ) : null}

        {data ? (
          <>
            <Text style={styles.kicker}>{today}</Text>
            <Text style={styles.title}>
              {data.panchang.paksha} {data.panchang.tithi}
            </Text>
            <Text style={styles.subtitle}>
              Moon in {data.moon_rashi} · {data.moon_nakshatra}
            </Text>

            <View style={styles.section}>
              <Label>Panchang now</Label>
              <Card>
                <Row
                  label="Tithi"
                  value={`${data.panchang.paksha} ${data.panchang.tithi}`}
                  hint={`${data.panchang.tithi_percent.toFixed(0)}% elapsed`}
                />
                <Row
                  label="Nakshatra"
                  value={data.panchang.nakshatra}
                  hint={`Pada ${data.panchang.nakshatra_pada}`}
                />
                <Row label="Yoga" value={data.panchang.yoga} />
                <Row label="Karana" value={data.panchang.karana} />
                <Row
                  label="Vara"
                  value={data.panchang.vara}
                  hint={`Ruled by ${data.panchang.vara_lord}`}
                />
                <Row label="Sun" value={data.sun_rashi} />
              </Card>
              <Text style={styles.caption}>
                Computed for {data.place ?? 'your birth place'} ({data.timezone}). A panchang
                belongs to a moment and a place, not to a person.
              </Text>
            </View>

            <View style={styles.section}>
              <Label>Your period</Label>
              <Card>
                {data.active.length === 0 ? (
                  <Text style={styles.empty}>Outside the computed 120-year cycle.</Text>
                ) : (
                  <View style={styles.track}>
                    {data.active.map((period, index) => (
                      <View key={`${period.lord}-${period.level}`} style={styles.step}>
                        <View style={styles.stepHead}>
                          <Text style={styles.stepLevel}>
                            {LEVELS[index] ?? `Level ${period.level}`}
                          </Text>
                          <Text style={styles.stepDates}>
                            {formatDate(period.start)} → {formatDate(period.end)}
                          </Text>
                        </View>
                        <Text style={styles.stepLord}>
                          {period.lord} <Text style={styles.stepLordHi}>{period.lord_hi}</Text>
                        </Text>
                      </View>
                    ))}
                  </View>
                )}
              </Card>
            </View>

            <View style={styles.section}>
              <Label>Against your birth</Label>
              <Card>
                <Row label="Moon then" value={data.birth_moon_rashi} />
                <Row label="Moon now" value={data.moon_rashi} />
                <Row label="Janma nakshatra" value={data.birth_nakshatra} />
              </Card>
              <Text style={styles.caption}>
                The sky above is the same for everyone alive right now. Only the second
                column is yours.
              </Text>
            </View>
          </>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  loading: { paddingVertical: space.xxl, alignItems: 'center' },
  retry: { marginTop: space.md },
  kicker: { ...type.label, color: colors.accent },
  title: { ...type.display, color: colors.text, marginTop: space.sm },
  subtitle: { ...type.body, color: colors.textMuted, marginTop: space.xs },
  section: { marginTop: space.xl },
  caption: { ...type.mono, color: colors.textFaint, marginTop: space.sm, lineHeight: 18 },
  empty: { ...type.body, color: colors.textMuted },
  track: { gap: space.md },
  step: {
    borderLeftWidth: 2,
    borderLeftColor: colors.accent,
    paddingLeft: space.md,
    paddingVertical: space.xs,
  },
  stepHead: { flexDirection: 'row', justifyContent: 'space-between', gap: space.sm },
  stepLevel: { ...type.label, color: colors.textFaint },
  stepDates: { ...type.mono, color: colors.textFaint },
  stepLord: { ...type.title, color: colors.text, marginTop: space.xs },
  stepLordHi: { ...type.body, color: colors.accentSoft },
});

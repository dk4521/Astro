/**
 * The chart screen — everything the engine knows, presented plainly.
 *
 * Note what is absent: no fear language, no dosha warnings, no ranking of
 * placements as lucky or unlucky. The screen states positions as measurements
 * and shows their provenance, which is the differentiation the product is built
 * on. Interpretation is a later layer, and it will translate this data rather
 * than invent alongside it.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import {
  ActivityIndicator,
  RefreshControl,
  ScrollView,
  StyleSheet,
  Text,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { fetchReading } from '../../src/api/client';
import { loadBirthDetails } from '../../src/api/storage';
import type { BirthDetails, DashaPeriod, Reading } from '../../src/api/types';
import { KundliChart } from '../../src/components/KundliChart';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, Chip, ErrorNote, Label, Row } from '../../src/components/ui';
import { colors, space, type } from '../../src/theme';

function formatDate(iso: string): string {
  const date = new Date(iso);
  return date.toLocaleDateString(undefined, {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function DashaTrack({ active }: { active: DashaPeriod[] }) {
  if (active.length === 0) {
    return <Text style={styles.empty}>Outside the computed 120-year cycle.</Text>;
  }

  const names = ['Mahadasha', 'Antardasha', 'Pratyantardasha'];

  return (
    <View style={styles.dashaTrack}>
      {active.map((period, index) => (
        <View key={`${period.lord}-${period.level}`} style={styles.dashaStep}>
          <View style={styles.dashaHeader}>
            <Text style={styles.dashaLevel}>{names[index] ?? `Level ${period.level}`}</Text>
            <Text style={styles.dashaDates}>
              {formatDate(period.start)} → {formatDate(period.end)}
            </Text>
          </View>
          <Text style={styles.dashaLord}>
            {period.lord} <Text style={styles.dashaLordHi}>{period.lord_hi}</Text>
          </Text>
        </View>
      ))}
    </View>
  );
}

export default function ChartScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();

  const [details, setDetails] = useState<BirthDetails | null>(null);
  const [reading, setReading] = useState<Reading | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [refreshing, setRefreshing] = useState(false);

  const load = useCallback(async (saved: BirthDetails) => {
    try {
      setReading(await fetchReading(saved, 3));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not compute your chart');
    }
  }, []);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const saved = await loadBirthDetails();
      if (cancelled) return;
      if (!saved) {
        router.replace('/onboarding');
        return;
      }
      setDetails(saved);
      await load(saved);
      if (!cancelled) setLoading(false);
    })();
    return () => {
      cancelled = true;
    };
  }, [load, router]);

  const refresh = useCallback(async () => {
    if (!details) return;
    setRefreshing(true);
    await load(details);
    setRefreshing(false);
  }, [details, load]);

  if (loading) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.accent} />
        <Text style={styles.loadingText}>Computing positions…</Text>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <ScreenHeader bordered={false} />
      <ScrollView
      style={styles.flex}
      contentContainerStyle={[
        styles.content,
        { paddingTop: space.md, paddingBottom: insets.bottom + space.xxl },
      ]}
      refreshControl={
        <RefreshControl
          refreshing={refreshing}
          onRefresh={refresh}
          tintColor={colors.accent}
        />
      }
    >
      {error ? (
        <View style={styles.section}>
          <ErrorNote message={error} />
          <View style={styles.retry}>
            <Button title="Try again" onPress={refresh} variant="ghost" />
          </View>
        </View>
      ) : null}

      {reading ? (
        <>
          <Text style={styles.kicker}>{details?.place ?? 'Your chart'}</Text>
          <Text style={styles.title}>
            {reading.chart.lagna.rashi} lagna
          </Text>
          <Text style={styles.subtitle}>
            Moon in {reading.chart.moon_rashi} · {reading.chart.janma_nakshatra}{' '}
            nakshatra
          </Text>

          <View style={styles.section}>
            <KundliChart chart={reading.chart} />
            <Text style={styles.caption}>
              North Indian chart · numbers are rashis, not houses
            </Text>
          </View>

          <View style={styles.section}>
            <Button title="Read my chart in words" onPress={() => router.push('/reading')} />
            <Text style={styles.caption}>
              Explained in plain language, then checked back against the numbers above.
            </Text>
          </View>

          <View style={styles.section}>
            <Label>Current period</Label>
            <Card>
              <DashaTrack active={reading.dasha.active} />
            </Card>
          </View>

          <View style={styles.section}>
            <Label>Grahas</Label>
            <Card>
              {reading.chart.grahas.map((graha, index) => (
                <View
                  key={graha.graha}
                  style={[styles.grahaRow, index > 0 && styles.divided]}
                >
                  <View style={styles.grahaName}>
                    <Text style={styles.grahaTitle}>{graha.graha}</Text>
                    <Text style={styles.grahaHi}>{graha.graha_hi}</Text>
                  </View>

                  <View style={styles.grahaFacts}>
                    <Text style={styles.grahaPosition}>
                      {graha.placement.rashi} {graha.placement.degree_dms}
                    </Text>
                    <Text style={styles.grahaMeta}>
                      House {graha.house} · {graha.placement.nakshatra} pada{' '}
                      {graha.placement.pada}
                    </Text>
                    {graha.retrograde || graha.combust ? (
                      <View style={styles.chips}>
                        {graha.retrograde ? <Chip text="RETRO" tone="retro" /> : null}
                        {graha.combust ? <Chip text="COMBUST" tone="combust" /> : null}
                      </View>
                    ) : null}
                  </View>
                </View>
              ))}
            </Card>
          </View>

          <View style={styles.section}>
            <Label>Panchang at birth</Label>
            <Card>
              <Row
                label="Tithi"
                value={`${reading.panchang.paksha} ${reading.panchang.tithi}`}
                hint={`${reading.panchang.tithi_percent.toFixed(1)}% elapsed`}
              />
              <Row
                label="Nakshatra"
                value={reading.panchang.nakshatra}
                hint={`Pada ${reading.panchang.nakshatra_pada}`}
              />
              <Row label="Yoga" value={reading.panchang.yoga} />
              <Row label="Karana" value={reading.panchang.karana} />
              <Row
                label="Vara"
                value={reading.panchang.vara}
                hint={`Ruled by ${reading.panchang.vara_lord}`}
              />
            </Card>
          </View>

          <View style={styles.section}>
            <Label>How this was computed</Label>
            <Card>
              <Row label="Ayanamsa" value={reading.chart.meta.ayanamsa_name}
                hint={`${reading.chart.meta.ayanamsa.toFixed(4)}°`} />
              <Row label="House system" value={reading.chart.meta.house_system} />
              <Row label="Ephemeris" value={reading.chart.meta.ephemeris_mode} />
              <Row label="Timezone" value={reading.chart.meta.timezone} />
              <Row
                label="Julian day (UT)"
                value={reading.chart.meta.julian_day.toFixed(6)}
              />
            </Card>
            <Text style={styles.caption}>
              Every value above is arithmetic from your birth moment. Same input, same
              output, always.
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
  content: { paddingHorizontal: space.lg },
  loading: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    gap: space.md,
  },
  loadingText: { ...type.body, color: colors.textMuted },
  kicker: { ...type.label, color: colors.accent },
  title: { ...type.display, color: colors.text, marginTop: space.sm },
  subtitle: { ...type.body, color: colors.textMuted, marginTop: space.xs },
  section: { marginTop: space.xl },
  caption: {
    ...type.mono,
    color: colors.textFaint,
    marginTop: space.sm,
    textAlign: 'center',
    lineHeight: 18,
  },
  retry: { marginTop: space.md },
  empty: { ...type.body, color: colors.textMuted },
  grahaRow: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingVertical: space.md,
    gap: space.md,
  },
  divided: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border },
  grahaName: { flexShrink: 0 },
  grahaTitle: { ...type.heading, color: colors.text },
  grahaHi: { ...type.mono, color: colors.textFaint, marginTop: 2 },
  grahaFacts: { flex: 1, alignItems: 'flex-end' },
  grahaPosition: { ...type.body, color: colors.text, fontWeight: '600' },
  grahaMeta: { ...type.mono, color: colors.textMuted, marginTop: 2, textAlign: 'right' },
  chips: { flexDirection: 'row', gap: space.xs, marginTop: space.sm },
  dashaTrack: { gap: space.md },
  dashaStep: {
    borderLeftWidth: 2,
    borderLeftColor: colors.accent,
    paddingLeft: space.md,
    paddingVertical: space.xs,
  },
  dashaHeader: { flexDirection: 'row', justifyContent: 'space-between', gap: space.sm },
  dashaLevel: { ...type.label, color: colors.textFaint },
  dashaDates: { ...type.mono, color: colors.textFaint },
  dashaLord: { ...type.title, color: colors.text, marginTop: space.xs },
  dashaLordHi: { ...type.body, color: colors.accentSoft },
});

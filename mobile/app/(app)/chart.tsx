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
import { useCallback, useEffect, useRef, useState } from 'react';
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
import {
  loadBirthDetails,
  loadDisplayLanguage,
  saveDisplayLanguage,
} from '../../src/api/storage';
import type { BirthDetails, DashaPeriod, Reading } from '../../src/api/types';
import { localeFor, riseSet, strings, type DisplayLanguage } from '../../src/i18n';
import { KundliChart } from '../../src/components/KundliChart';
import { LanguagePicker } from '../../src/components/LanguagePicker';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, Chip, ErrorNote, Label, Row } from '../../src/components/ui';
import { colors, grahaColour, space, type } from '../../src/theme';

function formatDate(iso: string, language: DisplayLanguage): string {
  return new Date(iso).toLocaleDateString(localeFor(language), {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
  });
}

function DashaTrack({
  active,
  language,
}: {
  active: DashaPeriod[];
  language: DisplayLanguage;
}) {
  const t = strings(language);
  if (active.length === 0) {
    return <Text style={styles.empty}>{t.outsideCycle}</Text>;
  }

  const names = t.dashaLevels;

  return (
    <View style={styles.dashaTrack}>
      {active.map((period, index) => (
        <View key={`${period.lord}-${period.level}`} style={styles.dashaStep}>
          <View style={styles.dashaHeader}>
            <Text style={styles.dashaLevel}>{names[index] ?? String(period.level)}</Text>
            <Text style={styles.dashaDates}>
              {formatDate(period.start, language)} → {formatDate(period.end, language)}
            </Text>
          </View>
          <Text style={styles.dashaLord}>
            {language === 'hi' ? period.lord_hi : period.lord}{' '}
            <Text style={styles.dashaLordHi}>
              {language === 'hi' ? period.lord : period.lord_hi}
            </Text>
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
  // Undefined until the stored choice is read, so the screen never renders one
  // language and then swaps to the other a frame later.
  const [language, setLanguage] = useState<DisplayLanguage | undefined>(undefined);

  useEffect(() => {
    loadDisplayLanguage().then(setLanguage);
  }, []);

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const t = strings(language ?? 'en');

  // Read through a ref so `load` does not have to depend on the language and
  // refetch every time someone flips the toggle — the payload is identical in
  // both languages, which is the whole point of sending them together.
  const chartFailed = useRef(strings('en').chartFailed);
  chartFailed.current = t.chartFailed;

  const load = useCallback(async (saved: BirthDetails) => {
    try {
      setReading(await fetchReading(saved, 3));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : chartFailed.current);
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

  if (loading || language === undefined) {
    return (
      <View style={styles.loading}>
        <ActivityIndicator color={colors.accent} />
        <Text style={styles.loadingText}>{t.computing}</Text>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <ScreenHeader
        bordered={false}
        right={<LanguagePicker value={language} onChange={chooseLanguage} />}
      />
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
            <Button title={t.tryAgain} onPress={refresh} variant="ghost" />
          </View>
        </View>
      ) : null}

      {reading ? (
        <>
          <Text style={styles.kicker}>{details?.place ?? t.yourChart}</Text>
          <Text style={styles.title}>
            {t.lagnaSuffix(
              language === 'hi' ? reading.chart.lagna.rashi_hi : reading.chart.lagna.rashi,
            )}
          </Text>
          <Text style={styles.subtitle}>
            {t.moonLine(
              language === 'hi' ? reading.chart.moon_rashi_hi : reading.chart.moon_rashi,
              language === 'hi'
                ? reading.chart.janma_nakshatra_hi
                : reading.chart.janma_nakshatra,
            )}
          </Text>

          <View style={styles.section}>
            <KundliChart chart={reading.chart} />
            <Text style={styles.caption}>
              {t.chartCaptionOne}{'\n'}
              {t.chartCaptionTwo}
            </Text>
          </View>

          <View style={styles.section}>
            <Button title={t.readInWords} onPress={() => router.push('/reading')} />
            <Text style={styles.caption}>{t.readInWordsNote}</Text>
          </View>

          <View style={styles.section}>
            <Label>{t.currentPeriod}</Label>
            <Card>
              <DashaTrack active={reading.dasha.active} language={language} />
            </Card>
          </View>

          <View style={styles.section}>
            <Label>{t.grahas}</Label>
            <Card>
              {reading.chart.grahas.map((graha, index) => (
                <View
                  key={graha.graha}
                  style={[styles.grahaRow, index > 0 && styles.divided]}
                >
                  <View style={styles.grahaName}>
                    {/* This list is the chart's legend, which is what turns the
                        colour up there into information rather than decoration.
                        A dot rather than coloured type: nine hues applied to
                        body text would cost more legibility than the tie-back
                        is worth. */}
                    <View style={styles.grahaTitleRow}>
                      <View
                        style={[
                          styles.grahaDot,
                          { backgroundColor: grahaColour[graha.graha] ?? colors.textFaint },
                        ]}
                      />
                      <Text style={styles.grahaTitle}>
                        {language === 'hi' ? graha.graha_hi : graha.graha}
                      </Text>
                    </View>
                    <Text style={styles.grahaHi}>
                      {language === 'hi' ? graha.graha : graha.graha_hi}
                    </Text>
                  </View>

                  <View style={styles.grahaFacts}>
                    <Text style={styles.grahaPosition}>
                      {language === 'hi' ? graha.placement.rashi_hi : graha.placement.rashi}{' '}
                      {graha.placement.degree_dms}
                    </Text>
                    <Text style={styles.grahaMeta}>
                      {t.houseLine(
                        graha.house,
                        language === 'hi'
                          ? graha.placement.nakshatra_hi
                          : graha.placement.nakshatra,
                        graha.placement.pada,
                      )}
                    </Text>
                    {graha.retrograde || graha.combust ? (
                      <View style={styles.chips}>
                        {graha.retrograde ? <Chip text={t.retro} tone="retro" /> : null}
                        {graha.combust ? <Chip text={t.combust} tone="combust" /> : null}
                      </View>
                    ) : null}
                  </View>
                </View>
              ))}
            </Card>
          </View>

          <View style={styles.section}>
            <Label>{t.panchangAtBirth}</Label>
            <Card>
              <Row
                label={t.tithi}
                value={
                  language === 'hi'
                    ? `${reading.panchang.paksha_hi} ${reading.panchang.tithi_hi}`
                    : `${reading.panchang.paksha} ${reading.panchang.tithi}`
                }
                hint={t.elapsed(reading.panchang.tithi_percent.toFixed(1))}
              />
              <Row
                label={t.nakshatra}
                value={
                  language === 'hi'
                    ? reading.panchang.nakshatra_hi
                    : reading.panchang.nakshatra
                }
                hint={t.pada(reading.panchang.nakshatra_pada)}
              />
              <Row
                label={t.yoga}
                value={language === 'hi' ? reading.panchang.yoga_hi : reading.panchang.yoga}
              />
              <Row
                label={t.karana}
                value={language === 'hi' ? reading.panchang.karana_hi : reading.panchang.karana}
              />
              <Row
                label={t.vara}
                value={language === 'hi' ? reading.panchang.vara_hi : reading.panchang.vara}
                hint={t.ruledBy(
                  language === 'hi'
                    ? reading.panchang.vara_lord_hi
                    : reading.panchang.vara_lord,
                )}
              />
                <Row
                  label={t.masa}
                  value={language === 'hi' ? reading.panchang.masa_hi : reading.panchang.masa}
                  hint={t.samvatValue(reading.panchang.vikram_samvat, reading.panchang.shaka_samvat)}
                />
                <Row
                  label={t.sunriseSet}
                  value={riseSet(reading.panchang.sunrise, reading.panchang.sunset, language, t.absent)}
                />
                <Row
                  label={t.moonriseSet}
                  value={riseSet(reading.panchang.moonrise, reading.panchang.moonset, language, t.absent)}
                />
            </Card>
          </View>

          <View style={styles.section}>
            <Label>{t.howComputed}</Label>
            <Card>
              <Row
                label={t.ayanamsa}
                value={
                  language === 'hi'
                    ? reading.chart.meta.ayanamsa_name_hi
                    : reading.chart.meta.ayanamsa_name
                }
                hint={`${reading.chart.meta.ayanamsa.toFixed(4)}°`}
              />
              <Row
                label={t.houseSystem}
                // The engine ships one house system and stamps it as
                // "whole-sign". Translating the value here rather than adding a
                // `house_system_hi` field keeps a constant out of the wire.
                value={
                  reading.chart.meta.house_system === 'whole-sign'
                    ? t.wholeSign
                    : reading.chart.meta.house_system
                }
              />
              <Row label={t.ephemeris} value={reading.chart.meta.ephemeris_mode} />
              <Row label={t.timezone} value={reading.chart.meta.timezone} />
              <Row label={t.julianDay} value={reading.chart.meta.julian_day.toFixed(6)} />
            </Card>
            <Text style={styles.caption}>{t.determinismNote}</Text>
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
  grahaTitleRow: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  grahaDot: { width: 8, height: 8, borderRadius: 4 },
  grahaTitle: { ...type.heading, color: colors.text },
  // Indented to clear the dot, so the Sanskrit name lines up under the English
  // one rather than under the swatch.
  grahaHi: { ...type.mono, color: colors.textFaint, marginTop: 2, marginLeft: 8 + space.sm },
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

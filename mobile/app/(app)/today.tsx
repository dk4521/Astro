/**
 * Home.
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
import { useCallback, useEffect, useRef, useState } from 'react';
import { ActivityIndicator, RefreshControl, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useRouter } from 'expo-router';

import { fetchToday } from '../../src/api/client';
import { loadTip } from '../../src/api/tip';
import {
  loadBirthDetails,
  loadDisplayLanguage,
  loadName,
  loadPersona,
  saveDisplayLanguage,
} from '../../src/api/storage';
import { PERSONAS, Portrait } from '../../src/components/Avatar';
import type { Today as TodayData, Tip } from '../../src/api/types';
import { localeFor, riseSet, strings, type DisplayLanguage } from '../../src/i18n';
import { LanguagePicker } from '../../src/components/LanguagePicker';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, ErrorNote, Label, Row } from '../../src/components/ui';
import { colors, radius, space, type } from '../../src/theme';

function formatDate(iso: string, language: DisplayLanguage): string {
  return new Date(iso).toLocaleDateString(localeFor(language), {
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
  const [language, setLanguage] = useState<DisplayLanguage | undefined>(undefined);
  const [name, setName] = useState('');
  const [companionId, setCompanionId] = useState<string | null>(null);

  // The daily line is a model call, so it is loaded apart from the panchang and
  // is allowed to fail on its own: an unreachable model must not take the whole
  // home screen down with it, since everything below the hook is arithmetic and
  // works offline.
  const [tip, setTip] = useState<Tip | null>(null);
  const [tipLoading, setTipLoading] = useState(false);
  const [tipFailed, setTipFailed] = useState(false);

  const router = useRouter();
  const companion = PERSONAS.find((p) => p.id === companionId) ?? null;

  useEffect(() => {
    loadDisplayLanguage().then(setLanguage);
    loadName().then(setName);
    loadPersona().then(setCompanionId);
  }, []);

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const t = strings(language ?? 'en');

  // Through a ref so flipping the toggle does not re-run the fetch: both
  // languages arrive in the same payload.
  const unreachable = useRef(strings('en').unreachable);
  unreachable.current = t.unreachable;

  const load = useCallback(async () => {
    try {
      const birth = await loadBirthDetails();
      if (!birth) return;
      setData(await fetchToday(birth));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : unreachable.current);
    } finally {
      setLoading(false);
    }
  }, []);

  /**
   * The daily line. Cached on the device for the day, so this is a read from
   * disk on every launch but the first — see `src/api/tip.ts`.
   *
   * `force` is what the Ask button and a failed first attempt use; an ordinary
   * focus never asks again, because asking again is what spends the quota.
   */
  const loadDailyTip = useCallback(
    async (lang: DisplayLanguage, who: string | null) => {
      const birth = await loadBirthDetails();
      if (!birth) return;
      setTipLoading(true);
      setTipFailed(false);
      try {
        setTip(await loadTip(birth, lang, who));
      } catch {
        // Deliberately quiet. The line is the nicest thing on the screen, not
        // the necessary one, and an error card where a greeting should be would
        // make a working home screen look broken.
        setTipFailed(true);
      } finally {
        setTipLoading(false);
      }
    },
    [],
  );

  useEffect(() => {
    if (!language) return;
    void loadDailyTip(language, companion?.name ?? null);
  }, [language, companion, loadDailyTip]);

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

  const today = new Date().toLocaleDateString(localeFor(language ?? 'en'), {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  return (
    <View style={styles.flex}>
      <ScreenHeader
        title={t.today}
        right={
          language ? <LanguagePicker value={language} onChange={chooseLanguage} /> : null
        }
      />

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
              <Button title={t.tryAgain} onPress={refresh} variant="ghost" />
            </View>
          </View>
        ) : null}

        {data ? (
          <>
            <Text style={styles.kicker}>{today}</Text>
            <Text style={styles.title}>
              {name ? t.greeting(name) : t.greetingNoName}
            </Text>

            {/* The hook. A generated line in the companion's voice, and one tap
                to keep talking to them about it. */}
            <View style={styles.hook}>
              <Text style={styles.hookLabel}>{t.cosmicVibe}</Text>

              <View style={styles.hookBody}>
                {companion ? (
                  <View style={styles.hookWho}>
                    <Portrait person={companion} size={34} />
                    <Text style={styles.hookName}>{companion.name}</Text>
                  </View>
                ) : null}

                {tipLoading && !tip ? (
                  <View style={styles.hookWaiting}>
                    <ActivityIndicator color={colors.textFaint} size="small" />
                  </View>
                ) : tip ? (
                  <Text style={styles.hookText}>{tip.text.trim()}</Text>
                ) : (
                  <Text style={styles.hookMuted}>{t.tipUnavailable}</Text>
                )}
              </View>

              <View style={styles.hookAction}>
                {tip ? (
                  <Button
                    title={
                      companion ? t.askAbout(companion.name) : t.askAboutNoCompanion
                    }
                    // Named a companion, so it must land on that companion —
                    // not on the picker.
                    onPress={() =>
                      router.push(companion ? '/reading?resume=1' : '/reading')
                    }
                  />
                ) : (
                  <Button
                    title={t.tipAsk}
                    onPress={() =>
                      language && loadDailyTip(language, companion?.name ?? null)
                    }
                    variant="ghost"
                    loading={tipLoading}
                  />
                )}
              </View>
            </View>

            <Text style={styles.subtitle}>
              {(language === 'hi'
                ? `${data.panchang.paksha_hi} ${data.panchang.tithi_hi}`
                : `${data.panchang.paksha} ${data.panchang.tithi}`) +
                ' · ' +
                t.moonLine(
                  language === 'hi' ? data.moon_rashi_hi : data.moon_rashi,
                  language === 'hi' ? data.moon_nakshatra_hi : data.moon_nakshatra,
                )}
            </Text>

            <View style={styles.section}>
              <Label>{t.yourPeriod}</Label>
              <Card>
                {data.active.length === 0 ? (
                  <Text style={styles.empty}>{t.outsideCycle}</Text>
                ) : (
                  <View style={styles.track}>
                    {data.active.map((period, index) => (
                      <View key={`${period.lord}-${period.level}`} style={styles.step}>
                        <View style={styles.stepHead}>
                          <Text style={styles.stepLevel}>
                            {t.dashaLevels[index] ?? String(period.level)}
                          </Text>
                          <Text style={styles.stepDates}>
                            {formatDate(period.start, language ?? 'en')} →{' '}
                            {formatDate(period.end, language ?? 'en')}
                          </Text>
                        </View>
                        <Text style={styles.stepLord}>
                          {language === 'hi' ? period.lord_hi : period.lord}{' '}
                          <Text style={styles.stepLordHi}>
                            {language === 'hi' ? period.lord : period.lord_hi}
                          </Text>
                        </Text>
                        {/* Only the mahadasha carries its theme. Repeating it
                            under all three levels turns a line worth reading
                            into wallpaper — and the backend only attaches it to
                            the periods a screen shows. */}
                        {index === 0 ? (
                          <Text style={styles.stepMeaning}>
                            {(language === 'hi' ? period.meaning_hi : period.meaning) ?? ''}
                          </Text>
                        ) : null}
                      </View>
                    ))}
                  </View>
                )}
              </Card>
            </View>

            <View style={styles.section}>
              <Label>{t.panchangNow}</Label>
              <Card>
                <Row
                  label={t.tithi}
                  value={
                    language === 'hi'
                      ? `${data.panchang.paksha_hi} ${data.panchang.tithi_hi}`
                      : `${data.panchang.paksha} ${data.panchang.tithi}`
                  }
                  hint={t.elapsed(data.panchang.tithi_percent.toFixed(0))}
                />
                <Row
                  label={t.nakshatra}
                  value={language === 'hi' ? data.panchang.nakshatra_hi : data.panchang.nakshatra}
                  hint={t.pada(data.panchang.nakshatra_pada)}
                />
                <Row
                  label={t.yoga}
                  value={language === 'hi' ? data.panchang.yoga_hi : data.panchang.yoga}
                />
                <Row
                  label={t.karana}
                  value={language === 'hi' ? data.panchang.karana_hi : data.panchang.karana}
                />
                <Row
                  label={t.vara}
                  value={language === 'hi' ? data.panchang.vara_hi : data.panchang.vara}
                  hint={t.ruledBy(
                    language === 'hi' ? data.panchang.vara_lord_hi : data.panchang.vara_lord,
                  )}
                />
                <Row
                  label={t.sun}
                  value={language === 'hi' ? data.sun_rashi_hi : data.sun_rashi}
                />
                <Row
                  label={t.masa}
                  value={language === 'hi' ? data.panchang.masa_hi : data.panchang.masa}
                  hint={t.samvatValue(data.panchang.vikram_samvat, data.panchang.shaka_samvat)}
                />
                <Row
                  label={t.sunriseSet}
                  value={riseSet(
                    data.panchang.sunrise,
                    data.panchang.sunset,
                    language ?? 'en',
                    t.absent,
                    data.timezone,
                  )}
                />
                <Row
                  label={t.moonriseSet}
                  value={riseSet(
                    data.panchang.moonrise,
                    data.panchang.moonset,
                    language ?? 'en',
                    t.absent,
                    data.timezone,
                  )}
                />
              </Card>
              <Text style={styles.caption}>
                {t.panchangPlaceNote(data.place ?? t.yourBirthPlace, data.timezone)}
              </Text>
            </View>

            <View style={styles.section}>
              <Label>{t.againstBirth}</Label>
              <Card>
                <Row
                  label={t.moonThen}
                  value={language === 'hi' ? data.birth_moon_rashi_hi : data.birth_moon_rashi}
                />
                <Row
                  label={t.moonNow}
                  value={language === 'hi' ? data.moon_rashi_hi : data.moon_rashi}
                />
                <Row
                  label={t.janmaNakshatra}
                  value={language === 'hi' ? data.birth_nakshatra_hi : data.birth_nakshatra}
                />
              </Card>
              <Text style={styles.caption}>{t.sharedSkyNote}</Text>
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

  // The hook. A sheet of glass with an accent edge — the one card on the screen
  // that is not a table, and the only place the app speaks rather than reports.
  hook: {
    marginTop: space.lg,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    borderLeftWidth: 3,
    borderLeftColor: colors.accent,
    borderRadius: radius.md,
    padding: space.md,
    gap: space.sm,
  },
  hookLabel: { ...type.label, color: colors.accentSoft },
  hookBody: { gap: space.sm },
  hookWho: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  // The name is an attribution beside the face, never a verb in a sentence:
  // Hindi has no ungendered "says", and five of the companions are men.
  hookName: { ...type.body, color: colors.text, fontWeight: '600' },
  hookText: { ...type.body, color: colors.text, lineHeight: 24 },
  hookMuted: { ...type.body, color: colors.textMuted },
  hookWaiting: { paddingVertical: space.md, alignItems: 'flex-start' },
  hookAction: { marginTop: space.xs },
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
  stepMeaning: { ...type.body, color: colors.textMuted, marginTop: space.xs, lineHeight: 22 },
});

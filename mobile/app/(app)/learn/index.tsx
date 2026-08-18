/**
 * The course index.
 *
 * The content comes from the server (see `src/api/course.ts`), so this screen
 * has real loading and offline states — unlike a bundled course, which is why
 * the trade is worth naming: a smaller app, chapters that can be corrected
 * without a release, and a first read that needs the network.
 */

import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { loadCourseIndex } from '../../../src/api/course';
import { loadProgress } from '../../../src/api/storage';
import type { CourseIndex, CourseLanguage } from '../../../src/api/types';
import { ScreenHeader } from '../../../src/components/ScreenHeader';
import { Button, ErrorNote, Label } from '../../../src/components/ui';
import { colors, radius, space, type } from '../../../src/theme';

const LANGUAGES: { value: CourseLanguage; label: string }[] = [
  { value: 'en', label: 'English' },
  { value: 'hi', label: 'हिंदी' },
];

export default function LearnIndex() {
  const router = useRouter();
  const [language, setLanguage] = useState<CourseLanguage>('en');
  const [index, setIndex] = useState<CourseIndex | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [read, setRead] = useState<string[]>([]);

  const load = useCallback(async (lang: CourseLanguage) => {
    setLoading(true);
    try {
      setIndex(await loadCourseIndex(lang));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load the course');
    } finally {
      setLoading(false);
    }
  }, []);

  // Refetched on focus so a chapter marked read shows its tick straight away.
  useFocusEffect(
    useCallback(() => {
      let cancelled = false;
      loadProgress().then((slugs) => {
        if (!cancelled) setRead(slugs);
      });
      load(language);
      return () => {
        cancelled = true;
      };
    }, [language, load]),
  );

  const chapters = index?.chapters ?? [];
  const done = chapters.filter((c) => read.includes(c.slug)).length;
  const next = chapters.find((c) => !read.includes(c.slug));

  let lastPart: string | null = null;

  return (
    <View style={styles.flex}>
      <ScreenHeader
        title="Learn"
        right={
          <View style={styles.langGroup}>
            {LANGUAGES.map((option) => {
              const active = option.value === language;
              return (
                <Pressable
                  key={option.value}
                  accessibilityRole="button"
                  accessibilityState={{ selected: active }}
                  onPress={() => setLanguage(option.value)}
                  style={({ pressed }) => [
                    styles.lang,
                    active && styles.langActive,
                    pressed && styles.pressed,
                  ]}
                >
                  <Text style={[styles.langText, active && styles.langTextActive]}>
                    {option.label}
                  </Text>
                </Pressable>
              );
            })}
          </View>
        }
      />

      <ScrollView contentContainerStyle={styles.content}>
        <Text style={styles.kicker}>
          {language === 'hi' ? 'ज्योतिष, शुरू से' : 'Jyotisha, from the ground up'}
        </Text>
        <Text style={styles.blurb}>
          {language === 'hi'
            ? 'तीस अध्याय, बुनियादी से मध्यम तक। हर अध्याय एक विचार समझाता है और फिर उसे आपकी अपनी कुंडली में दिखाता है — वही गणना किए गए आँकड़े, कोई बनाया हुआ उदाहरण नहीं।'
            : 'Thirty chapters, basic to intermediate. Each explains an idea and then shows it in your own chart — the same computed numbers, not a generated example.'}
        </Text>

        {loading && !index ? (
          <View style={styles.loading}>
            <ActivityIndicator color={colors.accent} />
          </View>
        ) : null}

        {error && !index ? (
          <View style={styles.section}>
            <ErrorNote message={error} />
            <View style={styles.retry}>
              <Button title="Try again" onPress={() => load(language)} variant="ghost" />
            </View>
          </View>
        ) : null}

        {index ? (
          <>
            <View style={styles.progressCard}>
              <View style={styles.progressHead}>
                <Text style={styles.progressCount}>
                  {done} / {chapters.length}
                </Text>
                <Text style={styles.progressMeta}>~{index.total_minutes} min</Text>
              </View>
              <View style={styles.track}>
                <View
                  style={[
                    styles.fill,
                    { width: `${chapters.length ? (done / chapters.length) * 100 : 0}%` },
                  ]}
                />
              </View>
              {next ? (
                <Pressable
                  accessibilityRole="button"
                  onPress={() => router.push(`/learn/${next.slug}?language=${language}`)}
                  style={({ pressed }) => [styles.resume, pressed && styles.pressed]}
                >
                  <Text style={styles.resumeText}>
                    {done === 0
                      ? language === 'hi'
                        ? 'शुरू करें'
                        : 'Start'
                      : language === 'hi'
                        ? 'जारी रखें'
                        : 'Continue'}{' '}
                    — {next.title}
                  </Text>
                </Pressable>
              ) : (
                <Text style={styles.finished}>
                  {language === 'hi'
                    ? 'तीसों अध्याय पढ़ लिए। ये यहीं रहेंगे, लौटकर देखने के लिए।'
                    : 'All thirty read. They stay here to come back to.'}
                </Text>
              )}
            </View>

            {chapters.map((chapter) => {
              const isRead = read.includes(chapter.slug);
              const newPart = chapter.part !== lastPart;
              lastPart = chapter.part;
              return (
                <View key={chapter.slug}>
                  {newPart ? (
                    <View style={styles.partHeading}>
                      <Label>{chapter.part}</Label>
                    </View>
                  ) : null}
                  <Pressable
                    accessibilityRole="button"
                    onPress={() => router.push(`/learn/${chapter.slug}?language=${language}`)}
                    style={({ pressed }) => [styles.row, pressed && styles.pressed]}
                  >
                    <View style={[styles.badge, isRead && styles.badgeRead]}>
                      <Text style={[styles.number, isRead && styles.numberRead]}>
                        {isRead ? '✓' : chapter.number}
                      </Text>
                    </View>
                    <View style={styles.rowText}>
                      <Text style={styles.rowTitle}>{chapter.title}</Text>
                      <Text style={styles.rowSummary}>{chapter.summary}</Text>
                      <Text style={styles.rowMeta}>
                        {chapter.level} · {chapter.minutes} min
                      </Text>
                    </View>
                  </Pressable>
                </View>
              );
            })}
          </>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  langGroup: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: radius.pill,
    padding: 3,
    gap: 2,
  },
  lang: { paddingHorizontal: space.sm + 2, paddingVertical: space.xs + 2, borderRadius: radius.pill },
  langActive: { backgroundColor: colors.accentDim },
  langText: { fontSize: 12, fontWeight: '600', color: colors.textFaint },
  langTextActive: { color: colors.accentSoft },
  kicker: { ...type.title, color: colors.text },
  blurb: { ...type.body, color: colors.textMuted, lineHeight: 22, marginTop: space.sm },
  loading: { paddingVertical: space.xxl, alignItems: 'center' },
  section: { marginTop: space.xl },
  retry: { marginTop: space.md },
  progressCard: {
    marginTop: space.xl,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    padding: space.md,
    gap: space.sm,
  },
  progressHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  progressCount: { ...type.heading, color: colors.text },
  progressMeta: { ...type.mono, color: colors.textFaint },
  track: { height: 4, borderRadius: 2, backgroundColor: colors.border, overflow: 'hidden' },
  fill: { height: 4, backgroundColor: colors.accent, borderRadius: 2 },
  resume: {
    marginTop: space.sm,
    backgroundColor: colors.accentDim,
    borderRadius: radius.sm,
    paddingVertical: space.sm + 2,
    paddingHorizontal: space.md,
  },
  resumeText: { ...type.body, color: colors.accentSoft, fontWeight: '600' },
  finished: { ...type.mono, color: colors.textFaint, marginTop: space.xs },
  pressed: { opacity: 0.7 },
  partHeading: { marginTop: space.xl, marginBottom: space.xs },
  row: {
    flexDirection: 'row',
    gap: space.md,
    paddingVertical: space.md,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  badge: {
    width: 30,
    height: 30,
    borderRadius: 15,
    borderWidth: 1,
    borderColor: colors.border,
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 2,
  },
  badgeRead: { backgroundColor: colors.accentDim, borderColor: colors.accent },
  number: { ...type.mono, color: colors.textFaint },
  numberRead: { color: colors.accentSoft },
  rowText: { flex: 1 },
  rowTitle: { ...type.heading, color: colors.text },
  rowSummary: { ...type.body, color: colors.textMuted, marginTop: 2, lineHeight: 20 },
  rowMeta: { ...type.mono, color: colors.textFaint, marginTop: space.xs },
});

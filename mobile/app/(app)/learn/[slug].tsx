/**
 * One chapter, fetched from the server and cached on the device.
 *
 * The "in your chart" block arrives with the chapter: the backend computes it
 * from the birth details sent with the request, using the same engine that
 * draws the chart screen. No model is involved anywhere in this path, which is
 * why it needs no grounding check and costs nothing per reader.
 */

import { useLocalSearchParams, useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { loadChapter } from '../../../src/api/course';
import { loadBirthDetails, loadProgress, markChapterRead } from '../../../src/api/storage';
import { useSync } from '../../../src/sync/context';
import type { CourseChapter, CourseLanguage } from '../../../src/api/types';
import { ScreenHeader } from '../../../src/components/ScreenHeader';
import { Button, ErrorNote } from '../../../src/components/ui';
import { colors, radius, space, type } from '../../../src/theme';

export default function ChapterScreen() {
  const router = useRouter();
  const { slug, language } = useLocalSearchParams<{ slug: string; language?: string }>();
  const { pushChapterRead } = useSync();
  const lang: CourseLanguage = language === 'hi' ? 'hi' : 'en';

  const [chapter, setChapter] = useState<CourseChapter | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [read, setRead] = useState(false);

  const load = useCallback(async () => {
    if (!slug) return;
    setLoading(true);
    try {
      const birth = await loadBirthDetails();
      setChapter(await loadChapter(slug, lang, birth));
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not load this chapter');
    } finally {
      setLoading(false);
    }
  }, [slug, lang]);

  useEffect(() => {
    load();
    if (slug) loadProgress().then((slugs) => setRead(slugs.includes(slug)));
  }, [load, slug]);

  const finish = async () => {
    if (!chapter) return;
    await markChapterRead(chapter.slug);
    // Fire and forget, like every other push here: the tick is already saved on
    // the device, and the union merge notices anything that did not make it up.
    void pushChapterRead(chapter.slug);
    setRead(true);
    if (chapter.next_slug) router.replace(`/learn/${chapter.next_slug}?language=${lang}`);
    else router.replace('/learn');
  };

  return (
    <View style={styles.flex}>
      <ScreenHeader title={chapter ? `${chapter.number} / 30` : 'Learn'} />

      <ScrollView contentContainerStyle={styles.content}>
        {loading && !chapter ? (
          <View style={styles.loading}>
            <ActivityIndicator color={colors.accent} />
          </View>
        ) : null}

        {error && !chapter ? (
          <View>
            <ErrorNote message={error} />
            <View style={styles.retry}>
              <Button title="Try again" onPress={load} variant="ghost" />
            </View>
            <View style={styles.retry}>
              <Button
                title="All chapters"
                onPress={() => router.replace('/learn')}
                variant="ghost"
              />
            </View>
          </View>
        ) : null}

        {chapter ? (
          <>
            <Text style={styles.level}>
              {chapter.part} · {chapter.level} · {chapter.minutes} min
            </Text>
            <Text style={styles.title}>{chapter.title}</Text>
            <Text style={styles.summary}>{chapter.summary}</Text>

            {chapter.sections.map((section) => (
              <View key={section.heading} style={styles.section}>
                <Text style={styles.heading}>{section.heading}</Text>
                {section.body.map((paragraph) => (
                  <Text key={paragraph.slice(0, 40)} style={styles.paragraph}>
                    {paragraph}
                  </Text>
                ))}
                {section.aside ? (
                  <View style={styles.aside}>
                    <Text style={styles.asideText}>{section.aside}</Text>
                  </View>
                ) : null}
              </View>
            ))}

            {chapter.in_your_chart ? (
              <View style={styles.yours}>
                <Text style={styles.yoursLabel}>
                  {lang === 'hi' ? 'आपकी कुंडली में' : 'IN YOUR CHART'}
                </Text>
                <Text style={styles.yoursText}>{chapter.in_your_chart}</Text>
              </View>
            ) : null}

            <View style={styles.actions}>
              <Button
                title={
                  chapter.next_slug
                    ? lang === 'hi'
                      ? 'पढ़ लिया — आगे बढ़ें'
                      : 'Mark read and continue'
                    : lang === 'hi'
                      ? 'पढ़ लिया — समाप्त'
                      : 'Mark read and finish'
                }
                onPress={finish}
              />
              {read ? (
                <Text style={styles.readNote}>
                  {lang === 'hi' ? 'यह अध्याय आप पढ़ चुके हैं।' : 'You have read this chapter.'}
                </Text>
              ) : null}
              <Pressable
                accessibilityRole="button"
                onPress={() => router.replace('/learn')}
                style={({ pressed }) => [styles.back, pressed && styles.pressed]}
              >
                <Text style={styles.backText}>
                  {lang === 'hi' ? 'सभी अध्याय' : 'All chapters'}
                </Text>
              </Pressable>
            </View>
          </>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  loading: { paddingVertical: space.xxl, alignItems: 'center' },
  retry: { marginTop: space.md },
  level: { ...type.label, color: colors.accent },
  title: { ...type.display, color: colors.text, marginTop: space.sm },
  summary: { ...type.body, color: colors.textMuted, lineHeight: 22, marginTop: space.sm },
  section: { marginTop: space.xl, gap: space.md },
  heading: { ...type.heading, color: colors.text },
  paragraph: { ...type.body, color: colors.text, lineHeight: 24 },
  aside: {
    borderLeftWidth: 2,
    borderLeftColor: colors.border,
    paddingLeft: space.md,
    paddingVertical: space.xs,
  },
  asideText: { ...type.mono, color: colors.textMuted, lineHeight: 20 },
  yours: {
    marginTop: space.xxl,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.accent,
    borderRadius: radius.md,
    padding: space.md,
    gap: space.sm,
  },
  yoursLabel: { ...type.label, color: colors.accentSoft },
  yoursText: { ...type.body, color: colors.text, lineHeight: 24 },
  actions: { marginTop: space.xxl, gap: space.md },
  readNote: { ...type.mono, color: colors.textFaint, textAlign: 'center' },
  back: { alignItems: 'center', paddingVertical: space.sm },
  backText: { ...type.body, color: colors.textMuted },
  pressed: { opacity: 0.7 },
});

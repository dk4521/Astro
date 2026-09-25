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
      <ScreenHeader
        title={chapter ? `${chapter.number} / 38` : 'Learn'}
        // Not router.back(). A chapter is a drawer route, not a pushed screen,
        // and the drawer's navigate() does not add a history entry — so back()
        // lands on whatever drawer route was open before Learn. Verified on a
        // device: it went to Chart. Naming the destination is the only way this
        // arrow means the same thing every time.
        onBack={() => router.replace('/learn')}
      />

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
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  loading: { paddingVertical: space.xxl, alignItems: 'center' },
  retry: { marginTop: space.md },
  level: { ...type.label, color: 'rgba(255, 255, 255, 0.6)', fontSize: 15 },
  title: { ...type.display, color: '#FFFFFF', marginTop: space.sm, fontSize: 32, fontWeight: '700' },
  summary: {
    ...type.body,
    color: colors.textMuted,
    lineHeight: 22,
    marginTop: space.sm,
    backgroundColor: colors.glass,
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingVertical: space.sm + 2,
    overflow: 'hidden',
  },
  section: {
    marginTop: space.lg,
    gap: space.lg,
    backgroundColor: 'transparent',
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(255, 255, 255, 0.15)',
    paddingBottom: space.xl,
  },
  heading: { ...type.heading, color: '#FFFFFF', fontSize: 22, fontWeight: '600' },
  paragraph: { ...type.body, color: 'rgba(255, 255, 255, 0.9)', fontSize: 18, lineHeight: 28 },
  aside: {
    borderLeftWidth: 3,
    borderLeftColor: 'rgba(255, 255, 255, 0.3)',
    paddingLeft: space.md,
    paddingVertical: space.xs,
  },
  asideText: { ...type.mono, color: 'rgba(255, 255, 255, 0.7)', fontSize: 15, lineHeight: 22 },
  yours: {
    marginTop: space.xxl,
    backgroundColor: 'transparent',
    borderWidth: 1,
    borderColor: 'rgba(255, 255, 255, 0.15)',
    borderRadius: radius.lg,
    padding: space.lg,
    gap: space.md,
  },
  yoursLabel: { ...type.label, color: 'rgba(255, 255, 255, 0.5)', fontSize: 13, letterSpacing: 1 },
  yoursText: { ...type.body, color: '#FFFFFF', fontSize: 18, lineHeight: 28 },
  actions: { marginTop: space.xxl, gap: space.md },
  readNote: { ...type.mono, color: colors.textFaint, textAlign: 'center' },
  back: { alignItems: 'center', paddingVertical: space.sm },
  backText: { ...type.body, color: colors.textMuted },
  pressed: { opacity: 0.7 },
});

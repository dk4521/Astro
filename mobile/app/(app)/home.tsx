/**
 * Home — the app's destinations as cards you can see.
 *
 * The sidebar already lists all of this, and that was the problem: a drawer is
 * only discovered by people who go looking for a drawer. Someone opening the
 * app for the second time met whichever screen the router landed on and no
 * evidence that matching, tarot or the course existed. A grid says the whole
 * app out loud, once, where a person is deciding what to do.
 *
 * **Six cards, not eight.** History and Settings are sidebar rows and nothing
 * more. A hub earns its place by being the shortest route to the thing you came
 * to do, and neither of those is ever that thing — one is a filing cabinet and
 * the other is a drawer you open twice a year. Putting them here would cost two
 * of the six slots that carry the app's actual work.
 *
 * **Every card says something true about *this* phone.** A grid of static
 * labels is a menu; the point of these is that Chat knows who you talk to and
 * Chart knows your lagna. All of it is either already on the device or arrives
 * without blocking the paint — the blurb is what shows in the meantime, and
 * offline it is what shows for good.
 */

import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useRef, useState } from 'react';
import {
  LayoutChangeEvent,
  Pressable,
  StyleSheet,
  Text,
  View,
  useWindowDimensions,
} from 'react-native';
import Animated, {
  useAnimatedRef,
  useAnimatedScrollHandler,
  useSharedValue,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';

import {
  HOME_NAMESPACE,
  birthKey,
  pruneNamespace,
  readCache,
  writeCache,
} from '../../src/api/cache';
import { fetchReading, fetchToday } from '../../src/api/client';
import { loadCachedCourseIndex } from '../../src/api/course';
import {
  loadBirthDetails,
  loadDisplayLanguage,
  loadName,
  loadPersona,
  loadProgress,
  saveDisplayLanguage,
} from '../../src/api/storage';
import { PERSONAS } from '../../src/components/Avatar';
import { HubIcon } from '../../src/components/HubIcon';
import { LanguagePicker } from '../../src/components/LanguagePicker';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Welcome } from '../../src/components/Welcome';
import { DESTINATION } from '../../src/destinations';
import type { Today } from '../../src/api/types';
import { localeFor, riseSet, strings, type DisplayLanguage, type HubKey } from '../../src/i18n';
import { alpha, colors, radius, space, type } from '../../src/theme';

/**
 * The grid, laid out by hand rather than taken whole from `DESTINATIONS`.
 *
 * A hub is a curated page: which screens belong on it, and which of them is
 * worth a full row, are editorial questions that a list of every route in the
 * app cannot answer. `DESTINATIONS` still owns where each one goes and what
 * colour it is, so the two cannot disagree about anything they both know.
 */
const LAYOUT: { key: HubKey; span: 'full' | 'half' }[] = [
  { key: 'today', span: 'full' },
  { key: 'chart', span: 'half' },
  { key: 'chat', span: 'half' },
  { key: 'matching', span: 'half' },
  { key: 'tarot', span: 'half' },
  { key: 'learn', span: 'full' },
];

type Lagna = { en: string; hi: string };
type Progress = { done: number; total: number };

/**
 * Today, on the device's own calendar.
 *
 * Not `toISOString()`, which is the day in UTC: east of Greenwich that turns
 * over in the middle of the night, so an Indian reader opening the app before
 * half past five in the morning was handed the panchang cached the previous
 * evening — yesterday's sunrise, yesterday's tithi. `/v1/today` computes the
 * panchang for *now* at the reader's place, and this key has to change when
 * their day does, not when Greenwich's does.
 */
function localDay(): string {
  const now = new Date();
  const month = `${now.getMonth() + 1}`.padStart(2, '0');
  const day = `${now.getDate()}`.padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
}

export default function Home() {
  const router = useRouter();

  // Undefined until read, so the toggle does not flash the wrong side.
  const [language, setLanguage] = useState<DisplayLanguage | undefined>(undefined);
  const [name, setName] = useState('');
  const [companion, setCompanion] = useState<string | null>(null);
  const [lagna, setLagna] = useState<Lagna | null>(null);
  const [progress, setProgress] = useState<Progress | null>(null);
  const [today, setToday] = useState<Today | null>(null);

  // The hero is exactly one screenful — of the scroller, not of the window,
  // which stops above it under the header and below it at the navigation bar.
  // Measured rather than computed from insets, because the header's height is
  // the header's business.
  const window = useWindowDimensions();
  const [viewport, setViewport] = useState(window.height);
  const measure = (event: LayoutChangeEvent) => {
    const { height: h } = event.nativeEvent.layout;
    setViewport((previous) => (previous === h ? previous : h));
  };

  // On the UI thread, so the hero keeps up with the finger rather than with
  // React. Everything that reads it is a Reanimated style.
  const scrollY = useSharedValue(0);
  const onScroll = useAnimatedScrollHandler((event) => {
    scrollY.value = event.contentOffset.y;
  });

  /** So the hero's cue can take the page down rather than only describe it. */
  const scroller = useAnimatedRef<Animated.ScrollView>();
  const toGrid = useCallback(() => {
    scroller.current?.scrollTo({ y: viewport, animated: true });
  }, [scroller, viewport]);

  /**
   * The chart the lagna was fetched for, so the request happens once a session
   * rather than once a visit — and again, correctly, if the birth details are
   * edited in Settings, because then the key is a different one.
   */
  const fetchedFor = useRef<string | null>(null);
  /** The same, for the panchang — which is keyed by the day as well as the chart. */
  const panchangFor = useRef<string | null>(null);

  // On focus rather than on mount: this is the screen you come back to after
  // changing your name, your language or your companion, and a card still
  // showing the old one is the kind of staleness people notice immediately.
  //
  // The callback takes no dependencies on purpose. `useFocusEffect` re-runs
  // whenever its callback changes identity, not only on focus, so anything this
  // effect also *sets* must stay out of the list.
  useFocusEffect(
    useCallback(() => {
      let cancelled = false;

      (async () => {
        const [lang, who, persona] = await Promise.all([
          loadDisplayLanguage(),
          loadName(),
          loadPersona(),
        ]);
        if (cancelled) return;
        setLanguage(lang);
        setName(who);
        setCompanion(PERSONAS.find((p) => p.id === persona)?.name ?? null);

        // The course index is read from the cache and never fetched: someone who
        // has not opened Learn has no index and no progress, which is the right
        // thing to show them anyway.
        const [slugs, index] = await Promise.all([
          loadProgress(),
          loadCachedCourseIndex(lang ?? 'en'),
        ]);
        if (cancelled || !index) return;
        setProgress({
          done: index.chapters.filter((chapter) => slugs.includes(chapter.slug)).length,
          total: index.chapters.length,
        });
      })();

      (async () => {
        const birth = await loadBirthDetails();
        if (!birth || cancelled) return;

        const id = birthKey(birth);
        const key = `${HOME_NAMESPACE}lagna.${id}.v1`;

        const cached = await readCache<Lagna>(key);
        if (cached && !cancelled) setLagna(cached);

        if (fetchedFor.current === id) return;
        fetchedFor.current = id;
        try {
          // One level of dasha: the card wants a rashi, not a whole reading.
          const reading = await fetchReading(birth, 1);
          const next = { en: reading.chart.lagna.rashi, hi: reading.chart.lagna.rashi_hi };
          // Cached before the cancelled check, not after. Leaving the screen
          // while this was in flight used to throw the answer away with the
          // ref above still marking the chart as fetched, so nothing asked
          // again for the rest of the session and the card kept its blurb.
          await writeCache(key, next);
          if (cancelled) return;
          setLagna(next);
        } catch {
          // Deliberately quiet, and deliberately retryable. The blurb underneath
          // is a whole sentence on its own; a card on the home screen is not the
          // place to report that a request failed.
          fetchedFor.current = null;
        }
      })();

      (async () => {
        const birth = await loadBirthDetails();
        if (!birth || cancelled) return;

        // The day, on the reader's own calendar. Sunrise and sunset are the
        // same all day and the tithi is not, which is why this is the one cache
        // in the app whose key carries a date: it must be right on a relaunch
        // at breakfast and gone by the next morning.
        const day = localDay();
        const family = `${HOME_NAMESPACE}today.${birthKey(birth)}.`;
        const key = `${family}${day}.v1`;

        const cached = await readCache<Today>(key);
        if (cached && !cancelled) setToday(cached);

        if (panchangFor.current === key) return;
        panchangFor.current = key;
        try {
          const fresh = await fetchToday(birth);
          // Stored whether or not this screen is still listening, for the same
          // reason as the lagna above: the request is not made twice.
          await writeCache(key, fresh);
          // Yesterday's entry can never be asked for again.
          await pruneNamespace(family, key);
          if (cancelled) return;
          setToday(fresh);
        } catch {
          panchangFor.current = null;
        }
      })();

      return () => {
        cancelled = true;
      };
    }, []),
  );

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const t = strings(language ?? 'en');

  const date = new Date().toLocaleDateString(localeFor(language ?? 'en'), {
    weekday: 'long',
    day: 'numeric',
    month: 'long',
  });

  /** What a card says under its title, once it knows anything. */
  const subtitle = (key: HubKey): string => {
    if (key === 'chart' && lagna) return t.hubChartLagna(language === 'hi' ? lagna.hi : lagna.en);
    if (key === 'chat' && companion) return t.hubChatWith(companion);
    return t.hub[key].blurb;
  };

  return (
    <View style={styles.flex}>
      <ScreenHeader
        right={
          language ? <LanguagePicker value={language} onChange={chooseLanguage} /> : null
        }
      />

      <Animated.ScrollView
        ref={scroller}
        onLayout={measure}
        onScroll={onScroll}
        scrollEventThrottle={16}
        contentContainerStyle={styles.content}
      >
        <Welcome
          height={viewport}
          greeting={name ? t.welcomeGreeting(name) : t.welcomeGreetingNoName}
          tagline={t.welcomeTagline}
          cue={t.welcomeScroll}
          scrollY={scrollY}
          onCue={toGrid}
        />

        <View style={styles.page}>
        <Text style={styles.kicker}>{t.hubKicker}</Text>

        <View style={styles.grid}>
          {LAYOUT.map(({ key, span }) => {
            const destination = DESTINATION[key];
            const full = span === 'full';
            return (
              <Pressable
                key={key}
                accessibilityRole="button"
                accessibilityLabel={t.hub[key].title}
                onPress={() => router.navigate(destination.route as never)}
                style={({ pressed }) => [
                  styles.card,
                  full ? styles.cardFull : styles.cardHalf,
                  {
                    borderColor: alpha(destination.tint, 0.5),
                    // The bloom outside the border. Supported since RN 0.76 on
                    // the new architecture, which this app is on; where it is
                    // not, the coloured border and wash still carry the card.
                    boxShadow: `0 0 18px ${alpha(destination.tint, 0.22)}`,
                  },
                  pressed && styles.pressed,
                ]}
              >
                {/* The wash. Lit from the icon's corner so the card has a
                    direction, rather than being evenly tinted all over. */}
                <LinearGradient
                  colors={[alpha(destination.tint, 0.17), alpha(destination.tint, 0.02)]}
                  start={{ x: 0.05, y: 0 }}
                  end={{ x: 0.85, y: 1 }}
                  style={StyleSheet.absoluteFill}
                />

                <HubIcon name={key} tint={destination.tint} size={full ? 34 : 40} />

                <View style={styles.titleRow}>
                  <Text style={styles.emoji}>{destination.emoji}</Text>
                  <Text style={styles.cardTitle}>{t.hub[key].title}</Text>
                </View>

                <Text style={styles.cardBlurb}>
                  {key === 'today' ? date : subtitle(key)}
                </Text>

                {key === 'today' && today ? (
                  <View style={styles.meta}>
                    <Text style={styles.metaLine}>
                      {language === 'hi'
                        ? `${today.panchang.paksha_hi} ${today.panchang.tithi_hi} · ${today.panchang.nakshatra_hi}`
                        : `${today.panchang.paksha} ${today.panchang.tithi} · ${today.panchang.nakshatra}`}
                    </Text>
                    <View style={styles.metaRow}>
                      <Text style={styles.metaLabel}>{t.sunriseSet}</Text>
                      <Text style={styles.metaValue}>
                        {riseSet(
                          today.panchang.sunrise,
                          today.panchang.sunset,
                          language ?? 'en',
                          t.absent,
                          today.timezone,
                        )}
                      </Text>
                    </View>
                    <View style={styles.metaRow}>
                      <Text style={styles.metaLabel}>{t.moonriseSet}</Text>
                      <Text style={styles.metaValue}>
                        {riseSet(
                          today.panchang.moonrise,
                          today.panchang.moonset,
                          language ?? 'en',
                          t.absent,
                          today.timezone,
                        )}
                      </Text>
                    </View>
                  </View>
                ) : null}

                {key === 'learn' && progress ? (
                  <View style={styles.progress}>
                    <View style={styles.track}>
                      <View
                        style={[
                          styles.fill,
                          {
                            backgroundColor: destination.tint,
                            width: `${progress.total ? (progress.done / progress.total) * 100 : 0}%`,
                          },
                        ]}
                      />
                    </View>
                    <Text style={styles.progressText}>
                      {t.hubChapters(progress.done, progress.total)}
                    </Text>
                  </View>
                ) : null}
              </Pressable>
            );
          })}
        </View>
        </View>
      </Animated.ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  // No horizontal padding: the hero above is full-bleed, and the grid brings
  // its own in `page`.
  content: { paddingBottom: space.xxl },
  page: { paddingHorizontal: space.lg },
  kicker: { ...type.label, color: colors.accent },

  // Two columns without a column gap: `space-between` supplies the gutter from
  // whatever is left over, so the cards fit any screen width. A percentage
  // width plus a fixed gap overflows on a narrow phone and drops to one column.
  grid: {
    marginTop: space.md,
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between',
    rowGap: space.md,
  },
  card: {
    backgroundColor: colors.glass,
    borderWidth: 1.5,
    borderRadius: radius.lg,
    padding: space.md,
    gap: space.sm,
    // The wash is an absolutely-filled child, so it has to be clipped to the
    // same rounded corners as the border it sits inside.
    overflow: 'hidden',
  },
  cardHalf: { width: '48%', minHeight: 168 },
  cardFull: { width: '100%' },
  pressed: { opacity: 0.65 },

  titleRow: { flexDirection: 'row', alignItems: 'center', gap: space.xs + 2 },
  emoji: { fontSize: 15 },
  cardTitle: { ...type.heading, fontSize: 19, color: colors.text },
  cardBlurb: { ...type.body, fontSize: 13, color: colors.textMuted, lineHeight: 19 },

  // Panchang under the date. A hairline rather than a gap: the rows below it
  // are a different kind of thing from the greeting above, and on a card this
  // wide they need saying apart.
  meta: {
    marginTop: space.xs,
    paddingTop: space.sm,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    gap: space.xs + 1,
  },
  metaLine: { ...type.body, fontSize: 13, color: colors.text },
  metaRow: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  metaLabel: { ...type.label, fontSize: 10, color: colors.textFaint },
  metaValue: { ...type.mono, fontSize: 12, color: colors.textMuted },

  progress: { marginTop: space.xs, gap: space.xs + 2 },
  track: {
    height: 5,
    borderRadius: radius.pill,
    backgroundColor: colors.border,
    overflow: 'hidden',
  },
  fill: { height: '100%', borderRadius: radius.pill },
  progressText: { ...type.mono, fontSize: 12, color: colors.textFaint },
});

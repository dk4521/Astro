/**
 * All seventy-eight cards.
 *
 * Free, and deliberately so: this is written material, not generated text, so
 * it costs nothing to serve and cannot be wrong differently tomorrow than it
 * was today. It is also the honest answer to "where did that meaning come
 * from" — a reader who has just been handed the Ten of Swords can come here and
 * see the same words everyone else gets, rather than wondering what the app
 * decided about them personally.
 *
 * Downloaded rather than bundled, for the same reason the course is: seventy-
 * eight cards in two languages is weight on every install for text read a card
 * at a time, and a corrected line should not need an app release. Whatever has
 * been fetched is kept, so a second visit works on a train.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  ActivityIndicator,
  FlatList,
  Pressable,
  StyleSheet,
  Text,
  View,
} from 'react-native';

import { loadDisplayLanguage, saveDisplayLanguage } from '../../../src/api/storage';
import { loadTarotDeck } from '../../../src/api/tarot';
import type { TarotCard, TarotDeck } from '../../../src/api/types';
import { LanguagePicker } from '../../../src/components/LanguagePicker';
import { ScreenHeader } from '../../../src/components/ScreenHeader';
import { CardEmblem, cardColour, rankMark } from '../../../src/components/TarotCard';
import { Button, ErrorNote } from '../../../src/components/ui';
import { strings, type DisplayLanguage } from '../../../src/i18n';
import { colors, radius, space, type } from '../../../src/theme';

/** `null` is "everything"; `major` and the four suit ids are the real filters. */
type Filter = null | 'major' | string;

export default function TarotDeckScreen() {
  const router = useRouter();
  const [language, setLanguage] = useState<DisplayLanguage>('en');
  const [deck, setDeck] = useState<TarotDeck | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<Filter>(null);
  const [open, setOpen] = useState<string | null>(null);

  const t = strings(language);

  useEffect(() => {
    loadDisplayLanguage().then(setLanguage);
  }, []);

  const load = useCallback(async () => {
    setLoading(true);
    try {
      setDeck(await loadTarotDeck());
      setError(null);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.unreachable);
    } finally {
      setLoading(false);
    }
    // `t` is read for one fallback string and would otherwise re-fetch the deck
    // on every language switch, which both copies already contain.
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    void load();
  }, [load]);

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const cards = useMemo(() => {
    if (!deck) return [];
    if (filter === null) return deck.cards;
    if (filter === 'major') return deck.cards.filter((card) => card.arcana === 'major');
    return deck.cards.filter((card) => card.suit === filter);
  }, [deck, filter]);

  const filters: { id: Filter; label: string }[] = useMemo(
    () => [
      { id: null, label: t.tarotAll },
      { id: 'major', label: t.tarotMajor },
      ...(deck?.suits ?? []).map((suit) => ({
        id: suit.id as Filter,
        label: language === 'hi' ? suit.name_hi : suit.name,
      })),
    ],
    [deck, language, t],
  );

  return (
    <View style={styles.flex}>
      <ScreenHeader
        title={t.tarotDeckTitle}
        // Not router.back(). The deck is a drawer route rather than a pushed
        // screen, and the drawer's navigate() adds no history entry — so back()
        // lands on whichever drawer route was open before Tarot. Verified on a
        // device: it went to Chart, the same way `learn/[slug]` once did.
        onBack={() => router.replace('/tarot')}
        right={<LanguagePicker value={language} onChange={chooseLanguage} />}
      />

      {loading && !deck ? (
        <View style={styles.centre}>
          <ActivityIndicator color={colors.accent} />
        </View>
      ) : error && !deck ? (
        <View style={styles.centre}>
          <ErrorNote message={error} />
          <View style={styles.retry}>
            <Button title={t.tryAgain} onPress={load} variant="ghost" />
          </View>
        </View>
      ) : (
        <FlatList
          data={cards}
          keyExtractor={(card) => card.id}
          contentContainerStyle={styles.content}
          ListHeaderComponent={
            <View style={styles.header}>
              <Text style={styles.intro}>{t.tarotDeckIntro}</Text>
              <View style={styles.filters}>
                {filters.map((option) => {
                  const active = option.id === filter;
                  return (
                    <Pressable
                      key={String(option.id)}
                      accessibilityRole="button"
                      accessibilityState={{ selected: active }}
                      onPress={() => setFilter(option.id)}
                      style={({ pressed }) => [
                        styles.filter,
                        active && styles.filterActive,
                        pressed && styles.pressed,
                      ]}
                    >
                      <Text style={[styles.filterText, active && styles.filterTextActive]}>
                        {option.label}
                      </Text>
                    </Pressable>
                  );
                })}
              </View>
            </View>
          }
          renderItem={({ item }) => (
            <Row
              card={item}
              language={language}
              expanded={open === item.id}
              onPress={() => setOpen((current) => (current === item.id ? null : item.id))}
              uprightLabel={t.tarotUpright}
              reversedLabel={t.tarotReversed}
            />
          )}
        />
      )}
    </View>
  );
}

function Row({
  card,
  language,
  expanded,
  onPress,
  uprightLabel,
  reversedLabel,
}: {
  card: TarotCard;
  language: DisplayLanguage;
  expanded: boolean;
  onPress: () => void;
  uprightLabel: string;
  reversedLabel: string;
}) {
  const tint = cardColour(card);

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ expanded }}
      onPress={onPress}
      style={({ pressed }) => [styles.row, pressed && styles.pressed]}
    >
      <View style={styles.rowHead}>
        <View style={[styles.mark, { borderColor: `${tint}66` }]}>
          <CardEmblem card={card} size={28} />
          <Text style={[styles.rank, { color: tint }]}>{rankMark(card)}</Text>
        </View>

        <View style={styles.rowText}>
          <Text style={styles.name}>
            {language === 'hi' ? card.name_hi : card.name}
          </Text>
          <Text style={styles.keywords} numberOfLines={expanded ? undefined : 1}>
            {language === 'hi' ? card.keywords_hi : card.keywords}
          </Text>
        </View>
      </View>

      {expanded ? (
        <View style={styles.meanings}>
          <View>
            <Text style={[styles.orient, { color: tint }]}>{uprightLabel}</Text>
            <Text style={styles.meaning}>
              {language === 'hi' ? card.upright_hi : card.upright}
            </Text>
          </View>
          <View>
            <Text style={[styles.orient, { color: tint }]}>{reversedLabel}</Text>
            <Text style={styles.meaning}>
              {language === 'hi' ? card.reversed_hi : card.reversed}
            </Text>
          </View>
        </View>
      ) : null}
    </Pressable>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  centre: { flex: 1, alignItems: 'center', justifyContent: 'center', padding: space.lg },
  retry: { marginTop: space.md },
  content: { paddingHorizontal: space.lg, paddingBottom: space.xxl },
  pressed: { opacity: 0.6 },

  header: { gap: space.md, paddingBottom: space.md },
  intro: { ...type.body, color: colors.textMuted, lineHeight: 22 },
  filters: { flexDirection: 'row', flexWrap: 'wrap', gap: space.sm },
  filter: {
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.pill,
    paddingHorizontal: space.md,
    paddingVertical: 6,
  },
  filterActive: { borderColor: colors.accent, backgroundColor: colors.accentDim },
  filterText: { ...type.label, fontSize: 10, color: colors.textMuted },
  filterTextActive: { color: colors.text },

  row: {
    backgroundColor: colors.glass,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    padding: space.md,
    marginBottom: space.sm,
    gap: space.sm,
  },
  rowHead: { flexDirection: 'row', alignItems: 'center', gap: space.md },
  mark: {
    width: 44,
    height: 44,
    borderRadius: radius.sm,
    borderWidth: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  rank: { fontSize: 8, fontWeight: '700', letterSpacing: 0.6, marginTop: -3 },
  rowText: { flex: 1, gap: 2 },
  name: { ...type.heading, color: colors.text },
  keywords: { ...type.mono, color: colors.textFaint },

  meanings: { gap: space.md, paddingTop: space.xs },
  orient: { ...type.label, fontSize: 9, marginBottom: 2 },
  meaning: { ...type.body, color: colors.text, lineHeight: 22 },
});

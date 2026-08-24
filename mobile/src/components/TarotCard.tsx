/**
 * A card face, drawn rather than photographed.
 *
 * There is no art in this app and there deliberately isn't going to be:
 * seventy-eight illustrations is a licensing problem, a forty-megabyte install,
 * and — in a product whose whole visual argument is restraint — the fastest way
 * to end up looking like every other tarot app. So a face is built from the
 * three facts the backend already sends: the arcana, the suit and the number.
 *
 * The suit colours are the theme's four element lights, reused rather than
 * re-picked. Tarot's suits *are* the elements — Wands fire, Cups water, Swords
 * air, Pentacles earth — so the chart screen and this one end up saying "fire"
 * in the same colour, which is a coincidence worth keeping.
 *
 * **The flip is the feature.** Turning a card over is the entire ritual, and a
 * spread that arrives already face-up is a list. Each card waits face-down
 * until it is tapped. The animation drives opacity as well as `rotateY`,
 * because `backfaceVisibility` is the kind of thing that works on one platform
 * and silently shows both faces on the other.
 */

import { useEffect } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, {
  Easing,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withTiming,
} from 'react-native-reanimated';
import Svg, { Circle, Path, Polygon } from 'react-native-svg';

import type { TarotCard, TarotSuit } from '../api/types';
import { colors, elementGlow, radius, space, type } from '../theme';

/** Suit to element light. The mapping is tarot's own, not ours. */
const SUIT_COLOUR: Record<TarotSuit, string> = {
  wands: elementGlow.fire,
  cups: elementGlow.water,
  swords: elementGlow.air,
  pentacles: elementGlow.earth,
};

export function cardColour(card: TarotCard): string {
  return card.suit ? SUIT_COLOUR[card.suit] : colors.accentSoft;
}

const ROMAN: [number, string][] = [
  [10, 'X'],
  [9, 'IX'],
  [5, 'V'],
  [4, 'IV'],
  [1, 'I'],
];

function roman(value: number): string {
  if (value === 0) return '0';
  let rest = value;
  let out = '';
  for (const [amount, numeral] of ROMAN) {
    while (rest >= amount) {
      out += numeral;
      rest -= amount;
    }
  }
  return out;
}

/**
 * The mark in the corner: a roman numeral for the major arcana, and for a suit
 * the rank as a card player would write it.
 */
export function rankMark(card: TarotCard): string {
  if (card.arcana === 'major') return roman(card.number);
  if (card.number === 1) return 'A';
  if (card.number <= 10) return String(card.number);
  return ['P', 'Kn', 'Q', 'K'][card.number - 11];
}

/** The emblem in the middle. Four suits, plus a star for the major arcana.
 *  Exported because the deck browser wants the same mark at list size. */
export function CardEmblem({ card, size = 46 }: { card: TarotCard; size?: number }) {
  const tint = cardColour(card);
  const stroke = { stroke: tint, strokeWidth: 2, strokeLinecap: 'round' as const };

  return (
    <Svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {card.suit === 'wands' ? (
        <>
          <Path d="M9 40 L36 10" {...stroke} strokeWidth={2.6} />
          <Path d="M27 11 q6 -5 10 -2 q1 5 -4 8" {...stroke} />
        </>
      ) : card.suit === 'cups' ? (
        <>
          <Path d="M11 14 h26 a13 13 0 0 1 -26 0 z" {...stroke} />
          <Path d="M24 27 v9" {...stroke} />
          <Path d="M15 37 h18" {...stroke} />
        </>
      ) : card.suit === 'swords' ? (
        <>
          <Path d="M24 5 L28 13 V32 H20 V13 Z" {...stroke} />
          <Path d="M13 33 H35" {...stroke} />
          <Path d="M24 33 V42" {...stroke} />
        </>
      ) : card.suit === 'pentacles' ? (
        <>
          <Circle cx={24} cy={24} r={16} {...stroke} />
          <Polygon
            points="24,12 31.1,33.7 12.6,20.3 35.4,20.3 17,33.7"
            {...stroke}
            strokeWidth={1.6}
          />
        </>
      ) : (
        <>
          <Circle cx={24} cy={24} r={5} {...stroke} />
          <Path d="M24 3 V13 M24 35 V45 M3 24 H13 M35 24 H45" {...stroke} />
          <Path d="M10 10 L16 16 M32 32 L38 38 M38 10 L32 16 M16 32 L10 38" {...stroke} />
        </>
      )}
    </Svg>
  );
}

/** The back. Identical for every card, which is what makes a spread a spread. */
function Back() {
  return (
    <View style={styles.back}>
      <View style={styles.backInner}>
        <Svg width={40} height={40} viewBox="0 0 48 48" fill="none">
          <Circle cx={24} cy={24} r={13} stroke={colors.accent} strokeWidth={1.4} />
          <Circle cx={24} cy={24} r={5} stroke={colors.accentSoft} strokeWidth={1.4} />
          <Path
            d="M24 4 V11 M24 37 V44 M4 24 H11 M37 24 H44"
            stroke={colors.accent}
            strokeWidth={1.4}
            strokeLinecap="round"
          />
        </Svg>
      </View>
    </View>
  );
}

export function TarotCardFace({
  card,
  reversed,
  revealed,
  language,
  onPress,
  accessibilityLabel,
}: {
  card: TarotCard;
  reversed: boolean;
  revealed: boolean;
  language: 'en' | 'hi';
  onPress?: () => void;
  accessibilityLabel?: string;
}) {
  const progress = useSharedValue(revealed ? 1 : 0);

  useEffect(() => {
    progress.value = withTiming(revealed ? 1 : 0, {
      duration: 520,
      easing: Easing.out(Easing.cubic),
    });
  }, [revealed, progress]);

  // Two half-turns rather than one: the front starts at 180° and lands at 360°,
  // so the card keeps turning the same way instead of unwinding.
  const frontStyle = useAnimatedStyle(() => ({
    transform: [
      { perspective: 900 },
      { rotateY: `${interpolate(progress.value, [0, 1], [180, 360])}deg` },
    ],
    opacity: progress.value >= 0.5 ? 1 : 0,
  }));

  const backStyle = useAnimatedStyle(() => ({
    transform: [
      { perspective: 900 },
      { rotateY: `${interpolate(progress.value, [0, 1], [0, 180])}deg` },
    ],
    opacity: progress.value >= 0.5 ? 0 : 1,
  }));

  const tint = cardColour(card);
  const name = language === 'hi' ? card.name_hi : card.name;

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel={accessibilityLabel}
      accessibilityState={{ expanded: revealed }}
      onPress={onPress}
      disabled={!onPress}
      style={styles.slot}
    >
      <Animated.View style={[styles.card, styles.layer, backStyle]}>
        <Back />
      </Animated.View>

      <Animated.View
        style={[styles.card, styles.layer, styles.front, { borderColor: `${tint}55` }, frontStyle]}
      >
        {/* Only the art turns over. A real reversed card is upside down all the
            way, including its name — which is authentic and unreadable, and a
            label nobody can read is not a design decision worth defending. */}
        <View style={[styles.art, reversed && styles.upsideDown]}>
          <Text style={[styles.rank, { color: tint }]}>{rankMark(card)}</Text>
          <CardEmblem card={card} />
        </View>
        <Text style={styles.name} numberOfLines={2}>
          {name}
        </Text>
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  // The container the two faces are stacked in. `aspectRatio` rather than a
  // fixed height, so three cards across a 360dp phone and three across a
  // tablet are both the shape of a card.
  slot: { flex: 1, aspectRatio: 0.62 },
  layer: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backfaceVisibility: 'hidden',
  },
  card: {
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    backgroundColor: colors.glass,
    overflow: 'hidden',
  },
  front: {
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingVertical: space.sm,
    paddingHorizontal: space.xs,
  },
  art: { flex: 1, alignItems: 'center', justifyContent: 'center', gap: 2 },
  upsideDown: { transform: [{ rotate: '180deg' }] },
  rank: { ...type.label, fontSize: 10, letterSpacing: 1 },
  name: {
    fontSize: 10,
    lineHeight: 13,
    fontWeight: '600',
    color: colors.textMuted,
    textAlign: 'center',
  },

  back: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: colors.glassRaised,
    padding: space.xs,
  },
  // The inner rule is what makes a flat back read as a card back rather than as
  // an empty rectangle.
  backInner: {
    flex: 1,
    alignSelf: 'stretch',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'rgba(185, 174, 255, 0.28)',
    borderRadius: radius.sm,
  },
});

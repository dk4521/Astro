/**
 * A card face, drawn rather than photographed.
 *
 * There is no art in this app and there deliberately isn't going to be:
 * seventy-eight illustrations is a licensing problem, a forty-megabyte install,
 * and — in a product whose whole visual argument is restraint — the fastest way
 * to end up looking like every other tarot app. So a face is *built* from the
 * three facts the backend already sends: the arcana, the suit and the number.
 *
 * What makes it read as a real card is not the illustration, it is the
 * furniture around it. Every deck since the fifteenth century has the same
 * three things, and all three are generated here:
 *
 *   a gilt frame with corner marks, which is what says "card" before you have
 *   read anything on it;
 *
 *   the numeral in a band at the top and the name in a band at the foot —
 *   the layout Rider-Waite fixed and every deck since has copied;
 *
 *   and, on a numbered card, **the suit mark repeated as many times as the
 *   number says**, laid out in the columns a real pip card uses. Three of Cups
 *   has three cups on it. That is not decoration, it is the card.
 *
 * The suit colours are the theme's four element lights, reused rather than
 * re-picked. Tarot's suits *are* the elements — Wands fire, Cups water, Swords
 * air, Pentacles earth — so the chart screen and this one end up saying "fire"
 * in the same colour, which is a coincidence worth keeping. The gilt is the
 * same warm gold as the send button, for the same reason: a palette with one
 * more colour in it is a palette.
 *
 * **The flip is the feature.** Turning a card over is the entire ritual, and a
 * spread that arrives already face-up is a list. Each card waits face-down
 * until it is tapped. The animation drives opacity as well as `rotateY`,
 * because `backfaceVisibility` is the kind of thing that works on one platform
 * and silently shows both faces on the other.
 *
 * Only the big face animates. `CardEmblem` is the same art with the movement
 * and the pip repetition taken out, for the deck browser — seventy-eight rows
 * of shimmer is a battery complaint, and a pip grid at 22px is a smudge.
 */

import { useEffect } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import Animated, {
  Easing,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import Svg, { Circle, Ellipse, G, Path, Polygon, Rect } from 'react-native-svg';

import type { TarotCard, TarotSuit } from '../api/types';
import { colors, elementGlow, radius, space, type } from '../theme';

/** The gilt. One warm colour, at three weights. */
const GILT = 'rgba(232, 200, 119, 0.62)';
const GILT_SOFT = 'rgba(232, 200, 119, 0.26)';
const GILT_INK = '#E8C877';

type Palette = { ink: string; ground: readonly [string, string] };

/**
 * Suit to element light, and a ground with real colour in it.
 *
 * Each ground runs from the suit's own hue down into the app's night, so a
 * spread reads as four different cards rather than four dark rectangles — the
 * top of a Cups card is properly teal and the top of a Wands card is properly
 * warm. It stops short of a flat saturated fill, which is the red-and-yellow
 * astrology app the theme exists to avoid, and the gradient does the work
 * instead: colour where the eye lands, dark where the name has to be read.
 */
const PALETTE: Record<TarotSuit | 'major', Palette> = {
  // Matched by eye against the major arcana's violet rather than by hex value:
  // a navy at the same numeric lightness as a violet still reads as black next
  // to it, and a spread of one Swords card between two majors is exactly where
  // that shows.
  wands: { ink: elementGlow.fire, ground: ['#6E2E3C', '#241426'] },
  cups: { ink: elementGlow.water, ground: ['#12566B', '#101B2E'] },
  swords: { ink: elementGlow.air, ground: ['#26437F', '#121428'] },
  pentacles: { ink: elementGlow.earth, ground: ['#1C5A3B', '#0F1E24'] },
  major: { ink: colors.accentSoft, ground: ['#432A70', '#1A1030'] },
};

function paletteFor(card: TarotCard): Palette {
  return PALETTE[card.suit ?? 'major'];
}

export function cardColour(card: TarotCard): string {
  return paletteFor(card).ink;
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
 * The mark in the top band: a roman numeral for the major arcana, and for a
 * suit the rank as a card player would write it.
 */
export function rankMark(card: TarotCard): string {
  if (card.arcana === 'major') return roman(card.number);
  if (card.number === 1) return 'A';
  if (card.number <= 10) return String(card.number);
  return ['P', 'Kn', 'Q', 'K'][card.number - 11];
}

// --- The drawings -----------------------------------------------------------
//
// Everything below is drawn inside a 48×48 box and placed by `Piece`, so one
// shape serves as a lone Ace at sixty points and as one of ten pips at twelve.

type Ink = { stroke: string; strokeWidth: number; strokeLinecap: 'round'; strokeLinejoin: 'round' };

function ink(colour: string, width = 2.4): Ink {
  return { stroke: colour, strokeWidth: width, strokeLinecap: 'round', strokeLinejoin: 'round' };
}

/** Places a 48-box drawing at a point, at a size, in the parent's coordinates. */
function Piece({
  x,
  y,
  size,
  children,
}: {
  x: number;
  y: number;
  size: number;
  children: React.ReactNode;
}) {
  const scale = size / 48;
  return (
    <G transform={`translate(${x - size / 2}, ${y - size / 2}) scale(${scale})`}>{children}</G>
  );
}

/** One suit mark, in the 48-box. */
function SuitMark({ suit, colour, weight }: { suit: TarotSuit; colour: string; weight: number }) {
  const s = ink(colour, weight);

  if (suit === 'wands') {
    return (
      <>
        <Path d="M9 40 L36 10" {...s} />
        <Path d="M27 11 q6 -5 10 -2 q1 5 -4 8" {...s} strokeWidth={weight * 0.8} />
      </>
    );
  }
  if (suit === 'cups') {
    return (
      <>
        <Path d="M11 15 h26 a13 13 0 0 1 -26 0 z" {...s} />
        <Path d="M24 28 v8" {...s} />
        <Path d="M15 37 h18" {...s} />
      </>
    );
  }
  if (suit === 'swords') {
    return (
      <>
        <Path d="M24 5 L28 14 V31 H20 V14 Z" {...s} />
        <Path d="M13 32 H35" {...s} />
        <Path d="M24 32 V43" {...s} />
      </>
    );
  }
  return (
    <>
      <Circle cx={24} cy={24} r={16} {...s} />
      <Polygon
        points="24,12 31.1,33.7 12.6,20.3 35.4,20.3 17,33.7"
        {...s}
        strokeWidth={weight * 0.7}
        fill="none"
      />
    </>
  );
}

/**
 * The twenty-two, one drawing each.
 *
 * Kept to a few strokes apiece and chosen to match what the card *means* here
 * rather than what the traditional plate shows. Death is a scythe, not a
 * skeleton; the Devil is a chain with one link already open, which is the line
 * the deck actually writes for it. Nothing in this set is drawn to frighten
 * anyone, because nothing in this deck is written to.
 */
function MajorIcon({ number, colour }: { number: number; colour: string }) {
  const s = ink(colour, 2.2);
  const t = ink(colour, 1.6);

  switch (number) {
    case 0: // The Fool — a first step, a bundle, a sun that has already risen
      return (
        <>
          <Circle cx={19} cy={15} r={4} {...s} />
          <Path d="M19 20 v11 l-5 9 M19 31 l5 9" {...s} />
          <Path d="M29 11 L34 33" {...s} />
          <Circle cx={30} cy={10} r={3.5} {...t} />
        </>
      );
    case 1: // The Magician — the wand, and what is above it
      return (
        <>
          <Path d="M24 17 V41" {...s} />
          <Circle cx={20} cy={11} r={4} {...t} />
          <Circle cx={28} cy={11} r={4} {...t} />
        </>
      );
    case 2: // The High Priestess — two pillars, a crescent between
      return (
        <>
          <Path d="M12 12 V41 M36 12 V41" {...s} />
          <Path d="M26 18 a8 8 0 1 0 0 15 a9.5 9.5 0 1 1 0 -15" {...t} />
        </>
      );
    case 3: // The Empress — a crown, and something growing under it
      return (
        <>
          <Path d="M13 25 l3 -11 l8 7 l8 -7 l3 11 z" {...s} />
          <Path d="M24 29 v12 M24 34 l-5 -4 M24 34 l5 -4" {...t} />
        </>
      );
    case 4: // The Emperor — a throne
      return (
        <>
          <Path d="M14 41 V21 h20 v20" {...s} />
          <Path d="M14 21 l4 -7 h12 l4 7" {...s} />
        </>
      );
    case 5: // The Hierophant — the tiered crown and the two keys
      return (
        <>
          <Path d="M16 26 h16 M18 26 l1 -6 h10 l1 6 M21 20 l1 -5 h4 l1 5" {...s} />
          <Path d="M18 31 l12 10 M30 31 l-12 10" {...t} />
        </>
      );
    case 6: // The Lovers — two who meet, under a light
      return (
        <>
          <Circle cx={19} cy={30} r={8} {...s} />
          <Circle cx={29} cy={30} r={8} {...s} />
          <Path d="M24 8 v5 M17 11 l2 4 M31 11 l-2 4" {...t} />
        </>
      );
    case 7: // The Chariot
      return (
        <>
          <Path d="M12 29 h24 v9 h-24 z" {...s} />
          <Path d="M14 29 l4 -8 h12 l4 8" {...t} />
          <Circle cx={17} cy={42} r={3.5} {...t} />
          <Circle cx={31} cy={42} r={3.5} {...t} />
        </>
      );
    case 8: // Strength — the calm one, not the loud one
      return (
        <>
          <Circle cx={24} cy={30} r={9} {...s} />
          <Path d="M24 21 v-3 M15 24 l-3 -2 M33 24 l3 -2 M17 38 l-2 3 M31 38 l2 3" {...t} />
          <Circle cx={20} cy={11} r={3.5} {...t} />
          <Circle cx={28} cy={11} r={3.5} {...t} />
        </>
      );
    case 9: // The Hermit — one lamp, carried alone
      return (
        <>
          <Path d="M18 16 h12 v15 h-12 z M20 16 v-3 h8 v3" {...s} />
          <Path d="M24 20 v7 M21 23 h6" {...t} />
          <Path d="M37 12 V42" {...s} />
        </>
      );
    case 10: // Wheel of Fortune
      return (
        <>
          <Circle cx={24} cy={25} r={13} {...s} />
          <Path d="M24 12 V38 M11 25 H37 M15 16 L33 34 M33 16 L15 34" {...t} />
        </>
      );
    case 11: // Justice — the scales, level
      return (
        <>
          <Path d="M24 12 V36 M11 19 h26 M18 39 h12" {...s} />
          <Path d="M6 19 a5 5 0 0 0 10 0 M32 19 a5 5 0 0 0 10 0" {...t} />
        </>
      );
    case 12: // The Hanged Man — the pause, seen from the other way up
      return (
        <>
          <Path d="M10 11 h28" {...s} />
          <Path d="M24 11 V21" {...t} />
          <Path d="M24 21 V33" {...s} />
          <Circle cx={24} cy={38} r={5} {...s} />
          <Path d="M24 26 l-7 6 M24 26 l7 6" {...t} />
        </>
      );
    case 13: // Death — a scythe. An ending, and nothing ghoulish about it.
      return (
        <>
          <Path d="M13 42 L35 13" {...s} />
          <Path d="M35 13 a15 15 0 0 0 -17 5" {...s} />
        </>
      );
    case 14: // Temperance — the pour between two cups
      // Drawn as the suit's own chalice, half size, twice. Two triangles read
      // as two triangles; two cups read as the card.
      return (
        <>
          <Path d="M7 11 h14 a7 7 0 0 1 -14 0 z M14 18 v5 M10 23 h8" {...t} />
          <Path d="M27 28 h14 a7 7 0 0 1 -14 0 z M34 35 v5 M30 40 h8" {...t} />
          <Path d="M17 21 q7 7 14 6" {...t} />
        </>
      );
    case 15: // The Devil — a chain, and one link already open
      return (
        <>
          <Path d="M18 14 a6 8 0 1 0 0 13 a6 8 0 1 0 0 -13" {...s} />
          <Path d="M30 22 a6 8 0 1 1 0 13" {...s} />
        </>
      );
    case 16: // The Tower — the footing, and the flash that found it
      return (
        <>
          <Path d="M16 42 V21 h16 v21" {...s} />
          <Path d="M15 21 l9 -7 l9 7" {...s} />
          <Path d="M26 25 l-5 9 h6 l-4 8" {...t} />
        </>
      );
    case 17: // The Star
      return (
        <>
          <Path d="M24 8 V32 M12 20 H36 M16 12 L32 28 M32 12 L16 28" {...s} />
          <Path d="M12 38 h24 M15 43 h18" {...t} />
        </>
      );
    case 18: // The Moon — the half-light, between two towers
      return (
        <>
          <Path d="M27 12 a10 10 0 1 0 0 19 a12 12 0 1 1 0 -19" {...s} />
          <Path d="M9 42 V33 l4 -5 l4 5 v9 M31 42 V33 l4 -5 l4 5 v9" {...t} />
        </>
      );
    case 19: // The Sun
      return (
        <>
          <Circle cx={24} cy={24} r={9} {...s} />
          <Path
            d="M24 6 V11 M24 37 V42 M6 24 H11 M37 24 H42 M11 11 L15 15 M33 33 L37 37 M37 11 L33 15 M15 33 L11 37"
            {...t}
          />
        </>
      );
    case 20: // Judgement — the call, and hearing it
      return (
        <>
          <Path d="M24 11 v3" {...t} />
          <Path d="M15 33 a9 13 0 0 1 18 0 z" {...s} />
          <Path d="M12 33 h24" {...s} />
          <Circle cx={24} cy={38} r={2.6} {...t} />
          <Path d="M8 18 a8 8 0 0 0 -2 7 M40 18 a8 8 0 0 1 2 7" {...t} />
        </>
      );
    default: // 21, The World — the circle closed
      return (
        <>
          <Ellipse cx={24} cy={25} rx={12} ry={16} {...s} />
          <Circle cx={24} cy={19} r={3.5} {...t} />
          <Path d="M24 23 v9 M19 27 h10" {...t} />
        </>
      );
  }
}

/**
 * A court figure — the four ranks told apart by what is on their head.
 *
 * A Page is bare-headed, a Knight wears a helm with a plume, a Queen a round
 * three-point crown, a King a taller five-point one. Same silhouette
 * underneath, because they are the same person at four stages, which is what
 * the court is.
 */
function CourtFigure({ rank, colour }: { rank: number; colour: string }) {
  const s = ink(colour, 2.2);
  const t = ink(colour, 1.6);

  return (
    <>
      <Circle cx={24} cy={19} r={6} {...s} />
      <Path d="M12 44 q0 -13 12 -13 q12 0 12 13" {...s} />
      {rank === 11 ? (
        <Path d="M18 13 q6 -4 12 0" {...t} />
      ) : rank === 12 ? (
        <>
          <Path d="M17 13 q7 -5 14 0 v-1" {...t} />
          <Path d="M31 12 q6 -3 5 -8" {...t} />
        </>
      ) : rank === 13 ? (
        <Path d="M16 13 l2 -7 l6 4 l6 -4 l2 7 z" {...t} />
      ) : (
        <Path d="M15 13 l1 -9 l4 5 l4 -6 l4 6 l4 -5 l1 9 z" {...t} />
      )}
    </>
  );
}

// --- Pip layout -------------------------------------------------------------
//
// The columns a real numbered card uses: two files down the sides, and the odd
// one out in the middle. Cribbed from playing-card practice rather than
// invented, because a grid of N symbols laid out any other way is the thing
// that makes a generated card look generated.

const COLUMN = { left: 30, right: 70, centre: 50 };

function pips(n: number): { x: number; y: number }[] {
  const { left: l, right: r, centre: c } = COLUMN;
  const pair = (y: number) => [
    { x: l, y },
    { x: r, y },
  ];

  switch (n) {
    case 2:
      return [
        { x: c, y: 33 },
        { x: c, y: 97 },
      ];
    case 3:
      return [
        { x: c, y: 28 },
        { x: c, y: 65 },
        { x: c, y: 102 },
      ];
    case 4:
      return [...pair(36), ...pair(94)];
    case 5:
      return [...pair(32), { x: c, y: 65 }, ...pair(98)];
    case 6:
      return [...pair(28), ...pair(65), ...pair(102)];
    case 7:
      return [...pair(26), { x: c, y: 46 }, ...pair(65), ...pair(104)];
    case 8:
      return [...pair(24), ...pair(51), ...pair(79), ...pair(106)];
    case 9:
      return [...pair(24), ...pair(51), { x: c, y: 65 }, ...pair(79), ...pair(106)];
    default:
      return [
        ...pair(22),
        { x: c, y: 40 },
        ...pair(49),
        ...pair(76),
        { x: c, y: 90 },
        ...pair(103),
      ];
  }
}

function pipSize(n: number): number {
  if (n <= 3) return 30;
  if (n <= 5) return 26;
  if (n <= 7) return 23;
  return 19;
}

/** The whole illustration, in a 100×130 window. */
function CardArt({ card, colour }: { card: TarotCard; colour: string }) {
  if (card.arcana === 'major') {
    return (
      <Svg width="100%" height="100%" viewBox="0 0 100 130" fill="none">
        <Piece x={50} y={65} size={74}>
          <MajorIcon number={card.number} colour={colour} />
        </Piece>
      </Svg>
    );
  }

  const suit = card.suit as TarotSuit;

  if (card.number >= 11) {
    return (
      <Svg width="100%" height="100%" viewBox="0 0 100 130" fill="none">
        <Piece x={50} y={54} size={70}>
          <CourtFigure rank={card.number} colour={colour} />
        </Piece>
        <Piece x={50} y={106} size={30}>
          <SuitMark suit={suit} colour={colour} weight={3} />
        </Piece>
      </Svg>
    );
  }

  // The Ace is one mark, large, with the light behind it that every deck gives
  // the aces.
  if (card.number === 1) {
    return (
      <Svg width="100%" height="100%" viewBox="0 0 100 130" fill="none">
        <Circle cx={50} cy={65} r={40} stroke={colour} strokeWidth={1} opacity={0.28} />
        <Circle cx={50} cy={65} r={31} stroke={colour} strokeWidth={1} opacity={0.45} />
        <Piece x={50} y={65} size={58}>
          <SuitMark suit={suit} colour={colour} weight={2.6} />
        </Piece>
      </Svg>
    );
  }

  const size = pipSize(card.number);
  return (
    <Svg width="100%" height="100%" viewBox="0 0 100 130" fill="none">
      {pips(card.number).map((spot, index) => (
        <Piece key={index} x={spot.x} y={spot.y} size={size}>
          <SuitMark suit={suit} colour={colour} weight={3.2} />
        </Piece>
      ))}
    </Svg>
  );
}

/**
 * The same art at list size, with the pip repetition dropped.
 *
 * Ten pentacles at 22px is a smudge, so a numbered card shows one mark and
 * lets the numeral beside it carry the count. The deck browser is a list, and
 * a list wants a legible glyph rather than a faithful miniature.
 */
export function CardEmblem({ card, size = 46 }: { card: TarotCard; size?: number }) {
  const colour = cardColour(card);
  return (
    <Svg width={size} height={size} viewBox="0 0 48 48" fill="none">
      {card.arcana === 'major' ? (
        <MajorIcon number={card.number} colour={colour} />
      ) : card.number >= 11 ? (
        <CourtFigure rank={card.number} colour={colour} />
      ) : (
        <SuitMark suit={card.suit as TarotSuit} colour={colour} weight={2.4} />
      )}
    </Svg>
  );
}

/**
 * The gilt: two rules and four corner marks.
 *
 * The rules are stretched to the card (`preserveAspectRatio="none"`), which is
 * fine for a rectangle and wrong for anything with a shape — so the corner
 * marks are four separate square canvases pinned to the corners instead. Drawn
 * inside one stretched viewBox they would have come out as four different
 * parallelograms, which is exactly the sort of detail that makes a generated
 * card look generated.
 */
function Corner({ style, rotate }: { style: object; rotate: string }) {
  return (
    <Svg
      width={11}
      height={11}
      viewBox="0 0 12 12"
      fill="none"
      style={[style, { transform: [{ rotate }] }]}
    >
      <Path d="M1 6 V1 H6" stroke={GILT} strokeWidth={1.3} strokeLinecap="round" />
    </Svg>
  );
}

function Frame() {
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <Svg
        style={StyleSheet.absoluteFill}
        width="100%"
        height="100%"
        viewBox="0 0 100 160"
        preserveAspectRatio="none"
        fill="none"
      >
        <Rect x={2.5} y={2.5} width={95} height={155} rx={6} stroke={GILT} strokeWidth={1.4} />
        <Rect x={6} y={6} width={88} height={148} rx={4} stroke={GILT_SOFT} strokeWidth={0.7} />
      </Svg>
      <Corner style={styles.cornerTL} rotate="0deg" />
      <Corner style={styles.cornerTR} rotate="90deg" />
      <Corner style={styles.cornerBR} rotate="180deg" />
      <Corner style={styles.cornerBL} rotate="270deg" />
    </View>
  );
}

/** The back. Identical for every card, which is what makes a spread a spread. */
function Back() {
  return (
    <LinearGradient
      colors={['#2A2050', '#171232']}
      start={{ x: 0.1, y: 0 }}
      end={{ x: 0.9, y: 1 }}
      style={styles.back}
    >
      <View style={styles.backInner}>
        <Svg width={44} height={44} viewBox="0 0 48 48" fill="none">
          <Circle cx={24} cy={24} r={14} stroke={GILT} strokeWidth={1.2} />
          <Circle cx={24} cy={24} r={8} stroke={colors.accentSoft} strokeWidth={1.2} />
          <Circle cx={24} cy={24} r={2.5} fill={GILT_INK} />
          <Path
            d="M24 3 V9 M24 39 V45 M3 24 H9 M39 24 H45 M9 9 L13 13 M35 35 L39 39 M39 9 L35 13 M13 35 L9 39"
            stroke={GILT_SOFT}
            strokeWidth={1.2}
            strokeLinecap="round"
          />
        </Svg>
      </View>
    </LinearGradient>
  );
}

export function TarotCardFace({
  card,
  reversed,
  revealed,
  language,
  index = 0,
  onPress,
  accessibilityLabel,
}: {
  card: TarotCard;
  reversed: boolean;
  revealed: boolean;
  language: 'en' | 'hi';
  /** Position in the spread, so three cards do not shimmer in lockstep. */
  index?: number;
  onPress?: () => void;
  accessibilityLabel?: string;
}) {
  const progress = useSharedValue(revealed ? 1 : 0);
  const sheen = useSharedValue(0);

  useEffect(() => {
    progress.value = withTiming(revealed ? 1 : 0, {
      duration: 560,
      easing: Easing.out(Easing.cubic),
    });
  }, [revealed, progress]);

  // A band of light crossing the face, the way a foiled card catches a lamp
  // when you tilt it. Staggered by position so the three cards in a spread do
  // not sweep in lockstep — three lights moving as one reads as a screen
  // effect, three moving apart reads as three objects.
  useEffect(() => {
    sheen.value = 0;
    sheen.value = withDelay(
      index * 900,
      withRepeat(
        withTiming(1, { duration: 3600, easing: Easing.inOut(Easing.quad) }),
        -1,
        false,
      ),
    );
  }, [sheen, index]);

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

  const sheenStyle = useAnimatedStyle(() => ({
    transform: [
      { translateX: interpolate(sheen.value, [0, 1], [-170, 170]) },
      { rotate: '18deg' },
    ],
    opacity: interpolate(sheen.value, [0, 0.2, 0.8, 1], [0, 0.9, 0.9, 0]),
  }));

  const palette = paletteFor(card);
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

      <Animated.View style={[styles.card, styles.layer, frontStyle]}>
        <LinearGradient
          colors={[...palette.ground]}
          start={{ x: 0.15, y: 0 }}
          end={{ x: 0.85, y: 1 }}
          style={styles.front}
        >
          <Animated.View style={[styles.sheen, sheenStyle]} pointerEvents="none">
            <LinearGradient
              colors={[
                'transparent',
                'rgba(255,255,255,0.10)',
                'rgba(255,236,190,0.30)',
                'rgba(255,255,255,0.10)',
                'transparent',
              ]}
              start={{ x: 0, y: 0 }}
              end={{ x: 1, y: 0 }}
              style={StyleSheet.absoluteFill}
            />
          </Animated.View>

          <Frame />

          <View style={styles.band}>
            <Text style={[styles.numeral, { color: GILT_INK }]}>{rankMark(card)}</Text>
          </View>

          {/* Only the illustration turns over. A real reversed card is upside
              down all the way, including its name — which is authentic and
              unreadable, and a label nobody can read is not a design decision
              worth defending. The band it sits in stays put, so the frame does
              not look like it fell over. */}
          <View style={[styles.art, reversed && styles.upsideDown]}>
            <CardArt card={card} colour={palette.ink} />
          </View>

          <View style={styles.plate}>
            <Text style={[styles.name, { color: palette.ink }]} numberOfLines={2}>
              {name}
            </Text>
          </View>
        </LinearGradient>
      </Animated.View>
    </Pressable>
  );
}

const styles = StyleSheet.create({
  // The container the two faces are stacked in. `aspectRatio` rather than a
  // fixed height, so three cards across a 360dp phone and three across a
  // tablet are both the shape of a card.
  slot: { flex: 1, aspectRatio: 0.6 },
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
    overflow: 'hidden',
  },
  front: {
    flex: 1,
    alignItems: 'center',
    paddingTop: space.xs + 2,
    paddingBottom: space.xs,
    paddingHorizontal: 5,
  },
  // Taller and wider than the card so the rotated band still covers the
  // corners at either end of its travel.
  sheen: { position: 'absolute', top: -50, bottom: -50, width: 64 },

  // The two ends of a card are bands, not floating captions. A sliver of
  // darkness behind them is what lets gold text sit over the bright top of a
  // gradient without going muddy.
  band: {
    alignSelf: 'stretch',
    alignItems: 'center',
    backgroundColor: 'rgba(10, 8, 18, 0.34)',
    borderRadius: radius.sm,
    paddingVertical: 1,
  },
  numeral: {
    ...type.label,
    fontSize: 9,
    letterSpacing: 1.4,
  },
  cornerTL: { position: 'absolute', top: 7, left: 7 },
  cornerTR: { position: 'absolute', top: 7, right: 7 },
  cornerBR: { position: 'absolute', bottom: 7, right: 7 },
  cornerBL: { position: 'absolute', bottom: 7, left: 7 },
  art: { flex: 1, alignSelf: 'stretch', paddingVertical: 2 },
  upsideDown: { transform: [{ rotate: '180deg' }] },

  // The name band. A hairline above it is what separates a title from a
  // caption sitting loose at the bottom of a picture.
  plate: {
    alignSelf: 'stretch',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: GILT_SOFT,
    backgroundColor: 'rgba(10, 8, 18, 0.34)',
    borderRadius: radius.sm,
    paddingTop: 3,
    paddingBottom: 1,
  },
  // `lineHeight` is 1.5x the size rather than the 1.3 a Latin face would take.
  // Devanagari carries marks above *and* below the line — छड़ियों has both — and
  // at 13 the second line's box collapsed to nothing on Android: "छड़ियों का
  // शिष्य" rendered as "छड़ियों का" with empty card below it, no ellipsis to
  // hint that anything was missing. Caught on a device; no typecheck would show
  // it, and the English names are all short enough never to wrap.
  //
  // `minHeight` reserves both lines whether or not a name uses them, so a
  // one-line name and a two-line name sit at the same height across a spread.
  name: {
    fontSize: 9.5,
    lineHeight: 15,
    minHeight: 30,
    fontWeight: '700',
    textAlign: 'center',
  },

  back: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 5,
  },
  // The inner rule is what makes a flat back read as a card back rather than
  // as an empty rectangle.
  backInner: {
    flex: 1,
    alignSelf: 'stretch',
    alignItems: 'center',
    justifyContent: 'center',
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: GILT_SOFT,
    borderRadius: radius.sm,
  },
});

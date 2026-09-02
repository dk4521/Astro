/**
 * Design tokens.
 *
 * The brief is a deliberate reaction against the red-and-yellow astrology app:
 * dark, calm, high contrast, generous space. Colours are muted and cool so the
 * one accent that does appear carries meaning rather than decoration.
 */

export const colors = {
  // Backgrounds, darkest to lightest.
  bg: '#0B0A14',
  surface: '#141222',
  surfaceRaised: '#1C1930',
  border: '#2A2640',

  // Text.
  text: '#F4F2FF',
  textMuted: '#A8A2C4',
  textFaint: '#6B6589',

  // Translucent surfaces. Every screen sits over the star field, so a card is
  // a sheet of glass rather than a fill: opaque enough that body text reads
  // cleanly, sheer enough that the sky behind it is still a sky.
  glass: 'rgba(26, 23, 48, 0.82)',
  glassRaised: 'rgba(40, 35, 72, 0.86)',
  glassBorder: 'rgba(185, 174, 255, 0.20)',

  // Accents. Used sparingly — a highlighted value, an active state.
  accent: '#8B7BF7',
  accentSoft: '#B9AEFF',
  accentDim: 'rgba(139, 123, 247, 0.14)',

  // Buttons. The three named ones carry meaning by colour — leaving and
  // entering an account, and sending. Everything else takes the brand gradient,
  // so the coloured ones stay the only coloured things on a screen.
  signOut: '#C1554D',
  signIn: '#1E7A5C',
  send: '#E8B84B',

  // Semantic. Never used to signal "good" or "bad" fortune, only chart facts
  // like retrograde motion — the product does not rank outcomes.
  retro: '#F0A868',
  combust: '#E4728F',
} as const;

/**
 * One colour per graha, for the chart.
 *
 * Identity, not judgement: the colour says *which* body this is, the way a
 * transit map colours a line rather than rating it. The hues follow the
 * traditional associations — Mangal red, Budha green, Shani's cold blue — but
 * desaturated into this palette, because nine saturated colours in a 320px
 * square is the red-and-yellow chart the theme exists to avoid.
 *
 * They are held apart in hue rather than in lightness, so the twelve houses
 * stay readable for a red-green colour-blind reader: Mars and Mercury differ in
 * lightness too, and every glyph carries its two-letter name regardless. Colour
 * here is a second channel on top of the label, never the only one.
 */
export const grahaColour: Record<string, string> = {
  Sun: '#F5A65B',
  Moon: '#DCEBF9',
  Mars: '#F5726B',
  Mercury: '#6FD2A8',
  Jupiter: '#F0D77F',
  Venus: '#F3B0D0',
  Saturn: '#8FAAE0',
  Rahu: '#AC98E6',
  Ketu: '#A9B2C6',
};

/**
 * The four elements, as light rather than paint.
 *
 * These are gradient stops, not fills — each house is lit from its own centre
 * and fades outward, which is what keeps twelve tinted cells from reading as
 * twelve blocks of colour. Flat fills were tried first and went muddy: a low
 * alpha of anything over this background turns to silt.
 *
 * Fire is deliberately pushed toward coral rather than orange. True orange over
 * a violet ground mixes to brown, which was the one genuinely ugly thing in the
 * first version of this chart.
 *
 * They carry a real fact rather than decorating: the twelve rashis cycle fire,
 * earth, air, water in order, so the wash tells you at a glance which trine a
 * house belongs to without printing another word in a cell that has no room.
 */
export const elementGlow = {
  fire: '#FF7E63',
  earth: '#7BD98F',
  air: '#79B4F5',
  water: '#57D0DC',
} as const;

/**
 * The same four for the rashi number, but lifted well above the wash.
 *
 * Not the glow colours themselves, which is what they were at first: a number
 * printed in its own element's hue sits on a cell lit by that same hue, so the
 * fire houses — the strongest wash — had the faintest numbers on them. Caught
 * on a phone, where the contrast is real rather than simulated. These are the
 * same four hues carried up in lightness until each one floats off its own
 * background.
 */
export const elementInk = {
  fire: '#FFB69B',
  earth: '#ADDDB4',
  air: '#ADCCF3',
  water: '#8EDCE5',
} as const;

/**
 * A palette hex at an alpha.
 *
 * Every tinted surface in the app is one colour at four or five opacities — a
 * border, a wash, a glow — and writing those as literal `rgba(...)` strings is
 * how a hue ends up subtly different in the one place somebody retyped it.
 * The tints are authored as `#RRGGBB`, which is the only form this accepts.
 */
export function alpha(hex: string, a: number): string {
  const n = parseInt(hex.slice(1), 16);
  return `rgba(${(n >> 16) & 255}, ${(n >> 8) & 255}, ${n & 255}, ${a})`;
}

/**
 * A palette hex, darkened.
 *
 * For the second stop of a button's gradient: one hue lit at the top and shaded
 * at the bottom is what makes a filled pill look like a surface rather than a
 * rectangle of paint, and deriving it means a tint only has to be chosen once.
 */
export function shade(hex: string, factor: number): string {
  const n = parseInt(hex.slice(1), 16);
  const f = (channel: number) => Math.max(0, Math.min(255, Math.round(channel * factor)));
  return `rgb(${f((n >> 16) & 255)}, ${f((n >> 8) & 255)}, ${f(n & 255)})`;
}

/**
 * How hard a tinted surface leans on its colour.
 *
 * Named rather than numeric at the call site, so a card on one screen and a
 * button on another cannot drift a hundredth apart. `wash` is deliberately
 * faint: body text sits on top of it, and a tint strong enough to notice on its
 * own is a tint strong enough to cost contrast.
 */
export const tintAlpha = {
  border: 0.45,
  glow: 0.18,
  wash: 0.13,
  washEnd: 0.02,
  ink: 0.9,
} as const;

/** The brand fill. Two stops, used through expo-linear-gradient. */
export const gradient = {
  brand: ['#9B8CFF', '#6B5BD6'] as const,
  /** For outline buttons, where the fill sits under text rather than behind it. */
  brandSoft: ['rgba(155, 140, 255, 0.22)', 'rgba(107, 91, 214, 0.16)'] as const,
};

export const space = {
  xs: 4,
  sm: 8,
  md: 16,
  lg: 24,
  xl: 32,
  xxl: 48,
} as const;

export const radius = {
  sm: 10,
  md: 16,
  lg: 24,
  pill: 999,
} as const;

export const type = {
  display: { fontSize: 34, fontWeight: '700' as const, letterSpacing: -0.8 },
  title: { fontSize: 24, fontWeight: '700' as const, letterSpacing: -0.4 },
  heading: { fontSize: 17, fontWeight: '600' as const, letterSpacing: -0.2 },
  body: { fontSize: 15, fontWeight: '400' as const },
  label: {
    fontSize: 11,
    fontWeight: '600' as const,
    letterSpacing: 1.2,
    textTransform: 'uppercase' as const,
  },
  mono: { fontSize: 13, fontWeight: '500' as const },
} as const;

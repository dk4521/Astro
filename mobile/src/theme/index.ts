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

  // Semantic. Never used to signal "good" or "bad" fortune, only chart facts
  // like retrograde motion — the product does not rank outcomes.
  retro: '#F0A868',
  combust: '#E4728F',
} as const;

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

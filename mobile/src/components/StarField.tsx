/**
 * The night sky behind a screen — drawn, tinted, and alive.
 *
 * Two reasons it is drawn rather than shipped as an image: an asset would have
 * to be authored at several densities to avoid soft stars on a modern phone,
 * and a fixed image cannot follow a screen that changes height.
 *
 * Positions come from a seeded generator evaluated once at module load, not
 * from `Math.random()` at render. A random field would reshuffle itself on
 * every re-render — a sky that rearranges when you tap a button reads as a
 * glitch rather than as a sky.
 *
 * The Milky Way band is a stack of radial gradients along a diagonal, with
 * dark-nebula patches cut into it and an extra-dense layer of micro stars
 * concentrated near the band centerline. This creates the dense, mottled
 * river of light visible in a real dark sky without shipping a multi-MB bitmap.
 *
 * The twinkle is per *layer*, not per star. Eight layers, each breathing on its
 * own period and phase, read as hundreds of stars twinkling independently while
 * costing eight animated nodes. The ~400 static micro stars cost zero animated
 * nodes. Everything here runs on Reanimated's UI thread, so a slow render never
 * stutters the sky.
 */

import { useEffect, useState } from 'react';
import { LayoutChangeEvent, StyleSheet, View, useWindowDimensions } from 'react-native';
import Animated, {
  Easing,
  Extrapolation,
  interpolate,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withTiming,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import Svg, { Circle, Defs, RadialGradient, Rect, Stop } from 'react-native-svg';

// ---------------------------------------------------------------------------
// Star colour palette
// ---------------------------------------------------------------------------

/**
 * Real stars are not white — they run from cool blue through white to warm
 * gold, and a nebula lends the faint ones its own pink. White is weighted
 * heaviest because a field of evenly mixed colour looks like confetti.
 *
 * Two warm tones (peach, cream) were added to balance the Milky Way's glow
 * so faint band stars look like they belong in the warmth rather than floating
 * above it.
 */
const TINTS = [
  '#FFFFFF',
  '#FFFFFF',
  '#FFFFFF',
  '#F4F2FF', // blue-white
  '#A8D8FF', // sky blue
  '#FFD6E8', // light pink
  '#FFE9B8', // pale gold
  '#D8C8FF', // soft violet
  '#B6F0E0', // faint teal
  '#FFE0D0', // warm peach
  '#E8DDD0', // soft cream
];

type Star = {
  /** Fractions of the viewport, so the field re-maps to any screen size. */
  x: number;
  y: number;
  r: number;
  opacity: number;
  color: string;
};

// ---------------------------------------------------------------------------
// Seeded random
// ---------------------------------------------------------------------------

/** Mulberry32 — small, and identical on every platform, which Math.random is not. */
function seeded(seed: number): () => number {
  return () => {
    seed |= 0;
    seed = (seed + 0x6d2b79f5) | 0;
    let t = Math.imul(seed ^ (seed >>> 15), 1 | seed);
    t = (t + Math.imul(t ^ (t >>> 7), 61 | t)) ^ t;
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

// ---------------------------------------------------------------------------
// Star generators
// ---------------------------------------------------------------------------

/** Build uniformly distributed stars with a natural cubic size curve. */
function build(count: number, seed: number): Star[] {
  const random = seeded(seed);
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    // Cubed, so most stars are faint pinpricks and a few are bright. An even
    // spread of sizes looks like scattered dots; this looks like a sky.
    const size = random() ** 3;
    stars.push({
      x: random(),
      y: random(),
      r: 0.5 + size * 1.7,
      opacity: 0.2 + random() * 0.6 + size * 0.2,
      color: TINTS[Math.floor(random() * TINTS.length)],
    });
  }
  return stars;
}

/** Build very small stars scattered uniformly — the static background dust. */
function buildMicro(count: number, seed: number): Star[] {
  const random = seeded(seed);
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    const size = random() ** 4;
    stars.push({
      x: random(),
      y: random(),
      r: 0.25 + size * 0.55,
      opacity: 0.06 + random() * 0.24 + size * 0.1,
      color: TINTS[Math.floor(random() * TINTS.length)],
    });
  }
  return stars;
}

/**
 * Build stars biased toward the Milky Way band.
 *
 * The band runs diagonally from upper-left (≈ 15 %, 0 %) to lower-right
 * (≈ 85 %, 100 %). 65 % of stars are placed near the centerline with a
 * rough gaussian perpendicular spread; the remainder scatter everywhere so
 * the field does not feel artificially empty outside the band.
 */
function buildBandBiased(count: number, seed: number): Star[] {
  const random = seeded(seed);
  const stars: Star[] = [];
  for (let i = 0; i < count; i++) {
    let x: number;
    let y: number;
    if (random() < 0.65) {
      // Place near the Milky Way band centerline.
      const t = random();
      const bandX = 0.15 + 0.7 * t;
      const bandY = t;
      // Rough gaussian via sum of three uniforms (central limit theorem lite).
      const offset = ((random() + random() + random()) / 3 - 0.5) * 0.28;
      // Perpendicular to direction (0.7, 1.0): (-1, 0.7) / √1.49 ≈ (-0.819, 0.574).
      x = Math.max(0, Math.min(1, bandX + offset * -0.819));
      y = Math.max(0, Math.min(1, bandY + offset * 0.574));
    } else {
      x = random();
      y = random();
    }
    const size = random() ** 4;
    stars.push({
      x,
      y,
      r: 0.25 + size * 0.55,
      opacity: 0.05 + random() * 0.22 + size * 0.1,
      color: TINTS[Math.floor(random() * TINTS.length)],
    });
  }
  return stars;
}

// ---------------------------------------------------------------------------
// Animated twinkle layers
// ---------------------------------------------------------------------------

type Layer = {
  stars: Star[];
  /** One full dim-to-bright sweep, in ms. */
  period: number;
  delay: number;
  min: number;
  max: number;
};

// Periods are deliberately not multiples of each other: any common factor and
// the layers would resynchronise every few seconds into one visible pulse.
const LAYERS: Layer[] = [
  { stars: build(30, 101), period: 2300, delay: 0, min: 0.35, max: 1 },
  { stars: build(28, 211), period: 3100, delay: 380, min: 0.45, max: 1 },
  { stars: build(26, 331), period: 4300, delay: 900, min: 0.28, max: 0.92 },
  { stars: build(24, 457), period: 5300, delay: 1500, min: 0.5, max: 1 },
  { stars: build(22, 587), period: 6700, delay: 2200, min: 0.25, max: 0.88 },
  { stars: build(20, 719), period: 7900, delay: 2900, min: 0.4, max: 1 },
  { stars: build(18, 853), period: 5800, delay: 3400, min: 0.3, max: 0.95 },
  { stars: build(16, 967), period: 8500, delay: 4100, min: 0.42, max: 0.96 },
];
// Animated total: 30+28+26+24+22+20+18+16 = 184

// ---------------------------------------------------------------------------
// Static star populations (no animation — zero Reanimated cost)
// ---------------------------------------------------------------------------

/** Micro stars concentrated in the Milky Way band — the river of light. */
const BAND_STARS = buildBandBiased(260, 1337);

/** Micro stars scattered everywhere — the faint background dust. */
const SCATTER_STARS = buildMicro(156, 4201);

/** All static stars, combined for a single SVG render pass. */
const ALL_STATIC: Star[] = [...BAND_STARS, ...SCATTER_STARS];
// Static total: 416. Grand total with animated: 600.

// ---------------------------------------------------------------------------
// Milky Way glow — radial gradients along the diagonal band
// ---------------------------------------------------------------------------

type GlowDef = {
  id: string;
  cx: string;
  cy: string;
  r: string;
  color: string;
  peak: number;
};

/**
 * Colours sit between warm amber and cool violet — not a warm sunset, not the
 * app's violet accent, but a dusty mauve-cream that could be either at a glance.
 * Alternating warm-leaning and cool-leaning stops keep the band from reading as
 * a single flat tone.
 */
const MILKY_WAY: GlowDef[] = [
  { id: 'mw0', cx: '18%', cy: '3%', r: '38%', color: '#C8BFD0', peak: 0.07 },
  { id: 'mw1', cx: '24%', cy: '14%', r: '34%', color: '#D0C8BF', peak: 0.09 },
  { id: 'mw2', cx: '30%', cy: '25%', r: '36%', color: '#C4BAC8', peak: 0.12 },
  { id: 'mw3', cx: '38%', cy: '35%', r: '38%', color: '#CFC5BE', peak: 0.14 },
  { id: 'mw4', cx: '46%', cy: '45%', r: '40%', color: '#C8BFC8', peak: 0.16 },
  { id: 'mw5', cx: '54%', cy: '55%', r: '40%', color: '#D2CAC0', peak: 0.15 },
  { id: 'mw6', cx: '62%', cy: '65%', r: '38%', color: '#C0B8C6', peak: 0.13 },
  { id: 'mw7', cx: '70%', cy: '76%', r: '35%', color: '#CBC2BA', peak: 0.10 },
  { id: 'mw8', cx: '78%', cy: '88%', r: '36%', color: '#C4BCC8', peak: 0.08 },
  { id: 'mw9', cx: '84%', cy: '97%', r: '34%', color: '#CCC4BE', peak: 0.06 },
];

// ---------------------------------------------------------------------------
// Dark dust lanes — negative space inside the Milky Way band
// ---------------------------------------------------------------------------

/**
 * The Great Rift and its cousins: where interstellar dust blocks the glow.
 * Without these the band reads as a plain stripe of light; with them it reads
 * as a cloud that has depth, which is what a real photograph of the Milky Way
 * looks like up close.
 */
type DarkLaneDef = {
  id: string;
  cx: string;
  cy: string;
  r: string;
  color: string;
  peak: number;
};

const DARK_LANES: DarkLaneDef[] = [
  { id: 'dl0', cx: '28%', cy: '20%', r: '13%', color: '#08061A', peak: 0.45 },
  { id: 'dl1', cx: '40%', cy: '38%', r: '10%', color: '#0A0818', peak: 0.38 },
  { id: 'dl2', cx: '50%', cy: '50%', r: '8%', color: '#08061A', peak: 0.32 },
  { id: 'dl3', cx: '58%', cy: '60%', r: '11%', color: '#0A0818', peak: 0.40 },
  { id: 'dl4', cx: '66%', cy: '73%', r: '9%', color: '#09071A', peak: 0.30 },
];

// ---------------------------------------------------------------------------
// Bright stars — a white core inside its own halo, breathing on its own clock
// ---------------------------------------------------------------------------

type Bright = {
  x: number;
  y: number;
  size: number;
  color: string;
  period: number;
  delay: number;
};

/**
 * Two of these (indices 2, 5) sit right on the Milky Way centerline so they
 * feel like the brightest stars in the band. The rest scatter into the dark
 * sky around it.
 */
const BRIGHT: Bright[] = [
  { x: 0.09, y: 0.07, size: 3.0, color: '#A8D8FF', period: 2900, delay: 0 },
  { x: 0.91, y: 0.13, size: 3.4, color: '#FFD6E8', period: 3700, delay: 600 },
  { x: 0.22, y: 0.22, size: 2.8, color: '#FFFFFF', period: 4600, delay: 1200 },
  { x: 0.94, y: 0.36, size: 3.1, color: '#FFE9B8', period: 5400, delay: 300 },
  { x: 0.08, y: 0.50, size: 2.8, color: '#D8C8FF', period: 4100, delay: 1900 },
  { x: 0.45, y: 0.44, size: 3.5, color: '#E8DDD0', period: 5800, delay: 900 },
  { x: 0.93, y: 0.61, size: 3.3, color: '#A8D8FF', period: 6200, delay: 800 },
  { x: 0.60, y: 0.68, size: 2.9, color: '#FFE0D0', period: 4800, delay: 2100 },
  { x: 0.05, y: 0.78, size: 2.9, color: '#FFD6E8', period: 5100, delay: 2400 },
  { x: 0.95, y: 0.88, size: 2.7, color: '#B6F0E0', period: 3300, delay: 1600 },
];

// ---------------------------------------------------------------------------
// Shooting stars
// ---------------------------------------------------------------------------

type Streak = {
  from: { x: number; y: number };
  to: { x: number; y: number };
  length: number;
  color: string;
  /** Full cycle including the wait. The streak itself occupies TRAVEL of it. */
  period: number;
  delay: number;
};

/** The fraction of a cycle the streak is actually crossing the sky. */
const TRAVEL = 0.15;

const STREAKS: Streak[] = [
  {
    from: { x: -0.15, y: 0.08 },
    to: { x: 0.75, y: 0.46 },
    length: 110,
    color: '#DCE9FF',
    period: 11000,
    delay: 2500,
  },
  {
    from: { x: 1.1, y: 0.22 },
    to: { x: 0.25, y: 0.72 },
    length: 86,
    color: '#FFD6E8',
    period: 17000,
    delay: 9000,
  },
];

// ---------------------------------------------------------------------------
// Nebula clouds — paired for balance, warm-violet blended
// ---------------------------------------------------------------------------

type Cloud = {
  id: string;
  cx: string;
  cy: string;
  r: string;
  color: string;
  peak: number;
  period: number;
  delay: number;
};

/**
 * Colours shifted from the original pure violet and pink toward a dusty
 * mauve-cream range — warm enough to complement the Milky Way glow, cool
 * enough to sit inside the violet theme. In pairs so no corner ends up
 * brighter than the corner opposite it.
 */
const CLOUDS: Cloud[] = [
  { id: 'violet', cx: '80%', cy: '8%', r: '58%', color: '#8B7BF7', peak: 0.16, period: 9000, delay: 0 },
  { id: 'violetLow', cx: '20%', cy: '92%', r: '58%', color: '#8B7BF7', peak: 0.16, period: 11500, delay: 4200 },
  { id: 'mauve', cx: '10%', cy: '30%', r: '45%', color: '#9B8AC0', peak: 0.11, period: 15000, delay: 5000 },
  { id: 'warmDust', cx: '90%', cy: '70%', r: '45%', color: '#BFA898', peak: 0.10, period: 12000, delay: 2000 },
];

// =========================================================================
// Components
// =========================================================================

function TwinkleLayer({
  layer,
  width,
  height,
}: {
  layer: Layer;
  width: number;
  height: number;
}) {
  const v = useSharedValue(layer.min);

  useEffect(() => {
    v.value = withDelay(
      layer.delay,
      // `true` reverses, so the layer fades back down instead of snapping — a
      // sawtooth here would look like a flicker, not a twinkle.
      withRepeat(
        withTiming(layer.max, { duration: layer.period, easing: Easing.inOut(Easing.sin) }),
        -1,
        true,
      ),
    );
  }, [layer.delay, layer.max, layer.period, v]);

  const style = useAnimatedStyle(() => ({ opacity: v.value }));

  return (
    <Animated.View style={[StyleSheet.absoluteFill, style]} pointerEvents="none">
      <Svg width={width} height={height}>
        {layer.stars.map((star, i) => (
          <Circle
            key={i}
            cx={star.x * width}
            cy={star.y * height}
            r={star.r}
            fill={star.color}
            fillOpacity={Math.min(star.opacity, 1)}
          />
        ))}
      </Svg>
    </Animated.View>
  );
}

/** Static micro stars — rendered once, no animation overhead whatsoever. */
function StaticStarField({
  stars,
  width,
  height,
}: {
  stars: Star[];
  width: number;
  height: number;
}) {
  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none">
      <Svg width={width} height={height}>
        {stars.map((star, i) => (
          <Circle
            key={i}
            cx={star.x * width}
            cy={star.y * height}
            r={star.r}
            fill={star.color}
            fillOpacity={Math.min(star.opacity, 1)}
          />
        ))}
      </Svg>
    </View>
  );
}

/**
 * The Milky Way glow and dark dust lanes.
 *
 * One very slow breathing animation (20 s full cycle, 85 %–100 % opacity range)
 * gives the band life without visibly pulsing. All ten glow gradients and five
 * dust lanes share this single animated node.
 */
function MilkyWayBand({
  width,
  height,
}: {
  width: number;
  height: number;
}) {
  const v = useSharedValue(0.85);

  useEffect(() => {
    v.value = withRepeat(
      withTiming(1, { duration: 20000, easing: Easing.inOut(Easing.sin) }),
      -1,
      true,
    );
  }, [v]);

  const style = useAnimatedStyle(() => ({ opacity: v.value }));

  return (
    <Animated.View style={[StyleSheet.absoluteFill, style]} pointerEvents="none">
      <Svg width={width} height={height}>
        <Defs>
          {MILKY_WAY.map((glow) => (
            <RadialGradient key={glow.id} id={glow.id} cx={glow.cx} cy={glow.cy} r={glow.r}>
              <Stop offset="0" stopColor={glow.color} stopOpacity={String(glow.peak)} />
              <Stop offset="0.45" stopColor={glow.color} stopOpacity={String(glow.peak * 0.45)} />
              <Stop offset="1" stopColor={glow.color} stopOpacity="0" />
            </RadialGradient>
          ))}
          {DARK_LANES.map((lane) => (
            <RadialGradient key={lane.id} id={lane.id} cx={lane.cx} cy={lane.cy} r={lane.r}>
              <Stop offset="0" stopColor={lane.color} stopOpacity={String(lane.peak)} />
              <Stop offset="0.6" stopColor={lane.color} stopOpacity={String(lane.peak * 0.3)} />
              <Stop offset="1" stopColor={lane.color} stopOpacity="0" />
            </RadialGradient>
          ))}
        </Defs>
        {MILKY_WAY.map((glow) => (
          <Rect key={`r${glow.id}`} x="0" y="0" width={width} height={height} fill={`url(#${glow.id})`} />
        ))}
        {DARK_LANES.map((lane) => (
          <Rect key={`r${lane.id}`} x="0" y="0" width={width} height={height} fill={`url(#${lane.id})`} />
        ))}
      </Svg>
    </Animated.View>
  );
}

/** A near star: a white core inside its own halo, breathing on its own clock. */
function BrightStar({
  star,
  index,
  width,
  height,
}: {
  star: Bright;
  index: number;
  width: number;
  height: number;
}) {
  const v = useSharedValue(0.3);

  useEffect(() => {
    v.value = withDelay(
      star.delay,
      withRepeat(
        withTiming(1, { duration: star.period, easing: Easing.inOut(Easing.quad) }),
        -1,
        true,
      ),
    );
  }, [star.delay, star.period, v]);

  // Scale as well as opacity: a star that only brightens looks like a lamp on a
  // dimmer, while one that also swells reads as atmosphere moving across it.
  const style = useAnimatedStyle(() => ({
    opacity: v.value,
    transform: [{ scale: 0.8 + v.value * 0.35 }],
  }));

  const box = star.size * 7;
  const gradientId = `halo${index}`;

  return (
    <Animated.View
      pointerEvents="none"
      style={[
        {
          position: 'absolute',
          left: star.x * width - box / 2,
          top: star.y * height - box / 2,
          width: box,
          height: box,
        },
        style,
      ]}
    >
      <Svg width={box} height={box}>
        <Defs>
          <RadialGradient id={gradientId} cx="50%" cy="50%" r="50%">
            <Stop offset="0" stopColor={star.color} stopOpacity="0.6" />
            <Stop offset="0.3" stopColor={star.color} stopOpacity="0.2" />
            <Stop offset="1" stopColor={star.color} stopOpacity="0" />
          </RadialGradient>
        </Defs>
        <Circle cx={box / 2} cy={box / 2} r={box / 2} fill={`url(#${gradientId})`} />
        <Circle cx={box / 2} cy={box / 2} r={star.size * 0.5} fill="#FFFFFF" fillOpacity={0.95} />
      </Svg>
    </Animated.View>
  );
}

function ShootingStar({
  streak,
  width,
  height,
}: {
  streak: Streak;
  width: number;
  height: number;
}) {
  const p = useSharedValue(0);

  useEffect(() => {
    // Does not reverse: a shooting star that rewinds is a rubber band.
    p.value = withDelay(
      streak.delay,
      withRepeat(
        withTiming(1, { duration: streak.period, easing: Easing.linear }),
        -1,
        false,
      ),
    );
  }, [p, streak.delay, streak.period]);

  const x0 = streak.from.x * width;
  const y0 = streak.from.y * height;
  const dx = streak.to.x * width - x0;
  const dy = streak.to.y * height - y0;
  const angle = (Math.atan2(dy, dx) * 180) / Math.PI;

  const style = useAnimatedStyle(() => {
    const t = interpolate(p.value, [0, TRAVEL], [0, 1], Extrapolation.CLAMP);
    return {
      // Fades in fast, holds, fades out — the streak should never blink out of
      // existence mid-sky.
      opacity: interpolate(
        p.value,
        [0, TRAVEL * 0.1, TRAVEL * 0.65, TRAVEL],
        [0, 1, 0.85, 0],
        Extrapolation.CLAMP,
      ),
      transform: [
        { translateX: x0 + dx * t },
        { translateY: y0 + dy * t },
        { rotate: `${angle}deg` },
      ],
    };
  });

  return (
    <Animated.View
      pointerEvents="none"
      style={[{ position: 'absolute', width: streak.length, height: 2 }, style]}
    >
      <LinearGradient
        // Tail first, head last: the bright end is the direction of travel.
        colors={['rgba(255,255,255,0)', streak.color]}
        start={{ x: 0, y: 0.5 }}
        end={{ x: 1, y: 0.5 }}
        style={styles.streak}
      />
    </Animated.View>
  );
}

/** Slow colour that keeps the field from reading as flat black. */
function NebulaCloud({
  cloud,
  width,
  height,
}: {
  cloud: Cloud;
  width: number;
  height: number;
}) {
  const v = useSharedValue(0.45);

  useEffect(() => {
    v.value = withDelay(
      cloud.delay,
      withRepeat(
        withTiming(1, { duration: cloud.period, easing: Easing.inOut(Easing.sin) }),
        -1,
        true,
      ),
    );
  }, [cloud.delay, cloud.period, v]);

  const style = useAnimatedStyle(() => ({ opacity: v.value }));

  return (
    <Animated.View style={[StyleSheet.absoluteFill, style]} pointerEvents="none">
      <Svg width={width} height={height}>
        <Defs>
          <RadialGradient id={cloud.id} cx={cloud.cx} cy={cloud.cy} r={cloud.r}>
            <Stop offset="0" stopColor={cloud.color} stopOpacity={String(cloud.peak)} />
            <Stop offset="1" stopColor={cloud.color} stopOpacity="0" />
          </RadialGradient>
        </Defs>
        <Rect x="0" y="0" width={width} height={height} fill={`url(#${cloud.id})`} />
      </Svg>
    </Animated.View>
  );
}

// =========================================================================
// Root
// =========================================================================

export function StarField() {
  // Measured, not taken from useWindowDimensions. Under Android's edge-to-edge
  // the window height stops above the navigation bar while this view fills the
  // whole screen, so sizing the SVG layers from it left the bottom strip with
  // no stars and no cloud at all — the base colour and nothing else. The gap
  // is invisible in a layout inspector and only shows up as a dead band.
  const window = useWindowDimensions();
  const [size, setSize] = useState({ width: window.width, height: window.height });

  const measure = (event: LayoutChangeEvent) => {
    const { width, height } = event.nativeEvent.layout;
    setSize((prev) => (prev.width === width && prev.height === height ? prev : { width, height }));
  };

  const { width, height } = size;

  return (
    <View style={StyleSheet.absoluteFill} pointerEvents="none" onLayout={measure}>
      {/* The void between stars. Darker than the original #191436 so the Milky
          Way glow has room to lift off the background — the contrast is what
          makes the band read as light rather than as a lighter shade of dark. */}
      <View style={styles.base} pointerEvents="none" />

      {/* Milky Way: the diagonal band of glow with dark dust lanes cut in. */}
      <MilkyWayBand width={width} height={height} />

      {/* Nebula clouds: subtle colour breathing at the corners and edges. */}
      {CLOUDS.map((cloud) => (
        <NebulaCloud key={cloud.id} cloud={cloud} width={width} height={height} />
      ))}

      {/* Static micro stars: ~400 tiny dots, many concentrated in the band.
          Zero animation cost — they render once and the native layer caches. */}
      <StaticStarField stars={ALL_STATIC} width={width} height={height} />

      {/* Animated twinkle layers: 184 stars across 8 layers. */}
      {LAYERS.map((layer, i) => (
        <TwinkleLayer key={i} layer={layer} width={width} height={height} />
      ))}

      {/* Bright stars with halos — the ten biggest points of light. */}
      {BRIGHT.map((star, i) => (
        <BrightStar key={i} star={star} index={i} width={width} height={height} />
      ))}

      {/* Shooting stars — two streaks on long, staggered cycles. */}
      {STREAKS.map((streak, i) => (
        <ShootingStar key={i} streak={streak} width={width} height={height} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  // The night itself. Darker than the original flat purple so the Milky Way
  // glow and nebula clouds have dynamic range to work with.
  base: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#0C0A18',
  },
  streak: { flex: 1, borderRadius: 1 },
});

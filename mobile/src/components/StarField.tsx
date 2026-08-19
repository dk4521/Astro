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
 * The twinkle is per *layer*, not per star. Six layers, each breathing on its
 * own period and phase, read as a hundred stars twinkling independently while
 * costing six animated nodes instead of a hundred and twenty-six. Everything
 * here runs on Reanimated's UI thread, so a slow render never stutters the sky.
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

/**
 * Real stars are not white — they run from cool blue through white to warm
 * gold, and a nebula lends the faint ones its own pink. White is weighted
 * heaviest because a field of evenly mixed colour looks like confetti.
 */
const TINTS = [
  '#FFFFFF',
  '#FFFFFF',
  '#FFFFFF',
  '#F2F0FF',
  '#A8D8FF', // sky blue
  '#FFD6E8', // light pink
  '#FFE9B8', // pale gold
  '#D8C8FF', // soft violet
  '#B6F0E0', // faint teal
];

type Star = {
  /** Fractions of the viewport, so the field re-maps to any screen size. */
  x: number;
  y: number;
  r: number;
  opacity: number;
  color: string;
};

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

function build(count: number, seed: number): Star[] {
  const random = seeded(seed);
  const stars: Star[] = [];
  for (let i = 0; i < count; i += 1) {
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
  { stars: build(26, 101), period: 2300, delay: 0, min: 0.38, max: 1 },
  { stars: build(24, 211), period: 3100, delay: 380, min: 0.5, max: 1 },
  { stars: build(22, 331), period: 4300, delay: 900, min: 0.3, max: 0.95 },
  { stars: build(20, 457), period: 5300, delay: 1500, min: 0.55, max: 1 },
  { stars: build(18, 587), period: 6700, delay: 2200, min: 0.28, max: 0.9 },
  { stars: build(16, 719), period: 7900, delay: 2900, min: 0.45, max: 1 },
];

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

type Bright = {
  x: number;
  y: number;
  size: number;
  color: string;
  period: number;
  delay: number;
};

const BRIGHT: Bright[] = [
  { x: 0.09, y: 0.09, size: 3.0, color: '#A8D8FF', period: 2900, delay: 0 },
  { x: 0.91, y: 0.15, size: 3.4, color: '#FFD6E8', period: 3700, delay: 600 },
  { x: 0.06, y: 0.27, size: 2.6, color: '#FFFFFF', period: 4600, delay: 1200 },
  { x: 0.94, y: 0.38, size: 3.1, color: '#FFE9B8', period: 5400, delay: 300 },
  { x: 0.08, y: 0.52, size: 2.8, color: '#D8C8FF', period: 4100, delay: 1900 },
  { x: 0.93, y: 0.63, size: 3.3, color: '#A8D8FF', period: 6200, delay: 800 },
  { x: 0.05, y: 0.79, size: 2.9, color: '#FFD6E8', period: 5100, delay: 2400 },
  { x: 0.95, y: 0.89, size: 2.7, color: '#B6F0E0', period: 3300, delay: 1600 },
];

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

// In pairs: each cloud faces one of the same colour and strength across the
// field, so no corner ends up brighter than the corner opposite it.
const CLOUDS: Cloud[] = [
  { id: 'violet', cx: '82%', cy: '8%', r: '62%', color: '#8B7BF7', peak: 0.24, period: 9000, delay: 0 },
  { id: 'violetLow', cx: '18%', cy: '92%', r: '62%', color: '#8B7BF7', peak: 0.24, period: 11500, delay: 4200 },
  { id: 'blue', cx: '8%', cy: '30%', r: '48%', color: '#63B3ED', peak: 0.14, period: 15000, delay: 5000 },
  { id: 'pink', cx: '92%', cy: '70%', r: '48%', color: '#FF9EC4', peak: 0.14, period: 12000, delay: 2000 },
];

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
      {/* One colour, top to bottom — the original top's own value. Three
          gradients were tried here and each disagreed with itself at the two
          ends: fading down went black, lifting the last stop went muddy, and
          matching the stops quietly raised the top as well. A flat base cannot
          drift. What depth there is comes from the clouds, placed in pairs. */}
      <View style={styles.base} pointerEvents="none" />

      {CLOUDS.map((cloud) => (
        <NebulaCloud key={cloud.id} cloud={cloud} width={width} height={height} />
      ))}

      {LAYERS.map((layer, i) => (
        <TwinkleLayer key={i} layer={layer} width={width} height={height} />
      ))}

      {BRIGHT.map((star, i) => (
        <BrightStar key={i} star={star} index={i} width={width} height={height} />
      ))}

      {STREAKS.map((streak, i) => (
        <ShootingStar key={i} streak={streak} width={width} height={height} />
      ))}
    </View>
  );
}

const styles = StyleSheet.create({
  // The night itself. Every screen in the app sits on this one value.
  base: {
    position: 'absolute',
    top: 0,
    left: 0,
    right: 0,
    bottom: 0,
    backgroundColor: '#191436',
  },
  streak: { flex: 1, borderRadius: 1 },
});

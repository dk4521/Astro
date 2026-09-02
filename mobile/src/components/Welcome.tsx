/**
 * The first screenful of the app.
 *
 * A hub is a good second thing to meet and a poor first one: eight labelled
 * boxes is a menu, and a menu is what you hand someone who already knows what
 * they came for. This is the sentence before the menu — the app's name, who it
 * is talking to, and what it does — and then it gets out of the way the moment
 * a thumb moves.
 *
 * **The Moon is a photograph, and the galaxy behind it is not.** The moon is a
 * real object with a real surface; nothing drawn in a hundred lines of SVG was
 * going to beat a picture of it, and the earlier attempt at one looked exactly
 * like what it was. The Milky Way is the opposite case — it has no edges and no
 * detail at this size, only light — so it is drawn, which means it costs a few
 * gradients instead of a second megabyte and lands at whatever size the screen
 * turns out to be.
 *
 * The photograph is cut out rather than laid down as a backdrop, which is what
 * lets the drawn sky be behind it rather than beside it.
 *
 * **The band is masked away from the Moon**, and that is astronomy rather than
 * taste: the galaxy is a hundred thousand light years behind it, so a wash of it
 * lying across the Moon's face would be light in front of the nearest object in
 * the sky. The mask is a hole the size of the disc.
 *
 * **Everything moves slowly and nothing loops visibly.** The photograph drifts,
 * the band breathes on a different clock, and the page scrolls them apart at
 * different rates. Three motions with no common period read as a sky; one read
 * as a screensaver.
 *
 * **This screen is allowed to be louder than the rest of the app.** The theme is
 * a deliberate reaction against the red-and-yellow astrology app, and every
 * other screen keeps to it: muted, calm, one accent that means something. A
 * cover is the exception that lets the rule hold — it spends the colour here so
 * that a highlighted value on the chart screen is still the only bright thing
 * there. Nothing in this file is exported, so the loudness cannot leak.
 */

import { useEffect, useMemo } from 'react';
import { Image, Pressable, StyleSheet, Text, View, useWindowDimensions } from 'react-native';
import Animated, {
  Easing,
  Extrapolation,
  interpolate,
  interpolateColor,
  useAnimatedStyle,
  useSharedValue,
  withDelay,
  withRepeat,
  withTiming,
  type SharedValue,
} from 'react-native-reanimated';
import { LinearGradient } from 'expo-linear-gradient';
import Svg, { Circle, Defs, G, Line, Mask, RadialGradient, Rect, Stop } from 'react-native-svg';

import { alpha, colors, radius, space, type } from '../theme';

const MOON = require('../../assets/moon.png');

/**
 * The Moon, cut out of the sky it was photographed against.
 *
 * The asset is the disc alone on transparency, not the original wallpaper. A
 * full frame would have had to cover the screen to avoid showing its own black
 * rectangle, which fixed the Moon at the width of the phone and hid everything
 * behind it — the app's own star field included. Cut out, it is an object with
 * a size, and the sky behind it is the app's.
 *
 * Its alpha comes from its brightness, so the unlit limb keeps the faint
 * presence it has in the photograph and the lit face stays solid. Solid
 * matters: a galaxy showing through the Moon's own surface would be worse than
 * no galaxy at all.
 */
const MOON_WIDTH = 0.546;
/** 811 ÷ 640, from the asset. The disc is a gibbous, so it is taller than wide. */
const MOON_ASPECT = 1.267;

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
// The near sky
// ---------------------------------------------------------------------------

/**
 * A second field of stars, for this screen only.
 *
 * The app already draws one behind every screen, and it is deliberately
 * restrained — text sits on top of it everywhere else. Nothing sits on top of
 * the middle of this one, so it can afford the density a real dark sky has.
 * These are extra, drawn in front of the app's own field and behind everything
 * else here.
 */
const HERO_TINTS = [
  '#FFFFFF',
  '#FFFFFF',
  '#F4F2FF', // blue-white
  '#CFE2FF', // sky blue
  '#FFE6C0', // pale gold
  '#E8D9FF', // pale violet
  '#FFD9E6', // nebula pink
];

type HeroStar = { x: number; y: number; r: number; o: number; tint: string };

/**
 * Four twinkle clocks, none of them a multiple of another.
 *
 * The breathing is per *layer*, not per star: forty stars sharing one clock
 * still read as forty stars twinkling, because the eye cannot hold forty
 * phases at once — and it costs four animated nodes instead of a hundred and
 * fifty.
 */
const TWINKLE = [
  { period: 2900, delay: 0, min: 0.42 },
  { period: 3700, delay: 640, min: 0.62 },
  { period: 4600, delay: 1480, min: 0.34 },
  { period: 6100, delay: 2260, min: 0.70 },
];

const HERO_STARS: HeroStar[][] = (() => {
  const random = seeded(70926);
  const layers: HeroStar[][] = TWINKLE.map(() => []);
  for (let i = 0; i < 152; i += 1) {
    layers[i % TWINKLE.length].push({
      x: random(),
      y: random(),
      // Cubed, so most are pinpricks and a few carry the field. A uniform
      // spread of sizes reads as gravel.
      r: 0.5 + random() ** 3 * 2.1,
      o: 0.4 + random() * 0.6,
      tint: HERO_TINTS[Math.floor(random() * HERO_TINTS.length)],
    });
  }
  return layers;
})();

/**
 * The handful of stars bright enough to have spikes.
 *
 * The spikes are a camera artefact, not something an eye sees — which is the
 * point: the Moon here is a photograph, so the sky it sits in should look
 * photographed too. Placed by hand rather than by the generator, because five
 * of them want to be spread around the frame and away from the disc, and five
 * is fewer than it takes to write a rule.
 */
const SPARKS = [
  { x: 0.14, y: 0.20, size: 15, tint: '#CFE2FF', period: 5200, delay: 0 },
  { x: 0.83, y: 0.29, size: 19, tint: '#FFE6C0', period: 6400, delay: 900 },
  { x: 0.09, y: 0.62, size: 13, tint: '#FFD9E6', period: 4700, delay: 2100 },
  { x: 0.90, y: 0.71, size: 16, tint: '#E8D9FF', period: 7100, delay: 1400 },
  { x: 0.30, y: 0.86, size: 12, tint: '#FFFFFF', period: 5800, delay: 3000 },
];

/**
 * How lit the sky is at a point — 0 against the Moon, 1 well clear of it.
 *
 * A gibbous Moon is the brightest thing in a night sky by a wide margin and it
 * washes out everything near it; photographs of one have a bare halo around the
 * disc. So this is not only a way of keeping stars off the Moon's face — though
 * it does that, and has to, because the unlit limb is semi-transparent and
 * would otherwise have stars showing through the Moon itself.
 */
function litness(dx: number, dy: number): number {
  const d = Math.hypot(dx, dy);
  return Math.min(1, Math.max(0, (d - 1) / 1.15));
}

function Sky({
  width,
  height,
  scrollY,
}: {
  width: number;
  height: number;
  scrollY: SharedValue<number>;
}) {
  // The disc's two half-axes, in pixels. Everything near it is measured
  // against these rather than against a circle, because it is not one.
  const a = (width * MOON_WIDTH) / 2;
  const b = a * MOON_ASPECT;

  const placed = useMemo(
    () =>
      HERO_STARS.map(layer =>
        layer
          .map(star => {
            const x = star.x * width;
            const y = star.y * height;
            return { ...star, x, y, o: star.o * litness((x - width / 2) / a, (y - height / 2) / b) };
          })
          // Dropped rather than drawn at zero: the ones behind the Moon can
          // never be seen, and not drawing them is the cheapest they get.
          .filter(star => star.o > 0.02),
      ),
    [a, b, height, width],
  );

  // The deepest layer, so it moves least and outlasts the rest. Parallax is
  // the whole trick by which a flat screen acquires a front and a back.
  const style = useAnimatedStyle(() => ({
    opacity: interpolate(scrollY.value, [0, height * 0.75], [1, 0], Extrapolation.CLAMP),
    transform: [
      { translateY: interpolate(scrollY.value, [0, height], [0, height * 0.03], Extrapolation.CLAMP) },
    ],
  }));

  return (
    <Animated.View pointerEvents="none" style={[StyleSheet.absoluteFill, style]}>
      {placed.map((stars, index) => (
        <StarLayer key={index} clock={TWINKLE[index]} stars={stars} width={width} height={height} />
      ))}
      {SPARKS.map((spark, index) => {
        const x = spark.x * width;
        const y = spark.y * height;
        return (
          <Sparkle
            key={index}
            spark={spark}
            x={x}
            y={y}
            lit={litness((x - width / 2) / a, (y - height / 2) / b)}
          />
        );
      })}
    </Animated.View>
  );
}

function StarLayer({
  clock,
  stars,
  width,
  height,
}: {
  clock: (typeof TWINKLE)[number];
  stars: HeroStar[];
  width: number;
  height: number;
}) {
  const v = useSharedValue(clock.min);

  useEffect(() => {
    v.value = withDelay(
      clock.delay,
      withRepeat(
        // Sine easing, not linear: a sawtooth reads as a flicker, and a
        // flickering star reads as a bug.
        withTiming(1, { duration: clock.period, easing: Easing.inOut(Easing.sin) }),
        -1,
        true,
      ),
    );
  }, [clock.delay, clock.period, v]);

  const style = useAnimatedStyle(() => ({ opacity: v.value }));

  return (
    <Animated.View pointerEvents="none" style={[StyleSheet.absoluteFill, style]}>
      <Svg width={width} height={height}>
        {stars.map((star, index) => (
          <Circle
            key={index}
            cx={star.x}
            cy={star.y}
            r={star.r}
            fill={star.tint}
            fillOpacity={star.o}
          />
        ))}
      </Svg>
    </Animated.View>
  );
}

/** One bright star: a halo, a core, and four spikes. */
function Sparkle({
  spark,
  x,
  y,
  lit,
}: {
  spark: (typeof SPARKS)[number];
  x: number;
  y: number;
  lit: number;
}) {
  const v = useSharedValue(0.5);

  useEffect(() => {
    v.value = withDelay(
      spark.delay,
      withRepeat(
        withTiming(1, { duration: spark.period, easing: Easing.inOut(Easing.sin) }),
        -1,
        true,
      ),
    );
  }, [spark.delay, spark.period, v]);

  const style = useAnimatedStyle(() => ({
    opacity: v.value * lit,
    // Barely a swell. Anything an eye can measure turns a star into a pulse.
    transform: [{ scale: 0.92 + v.value * 0.12 }],
  }));

  // Shorter and fainter than the first pass, which put five lens flares in a
  // frame that has one subject. A diffraction spike is a grace note.
  const box = spark.size * 5;
  const c = box / 2;
  const arm = spark.size * 1.9;
  const id = `sp${spark.period}`;

  return (
    <Animated.View
      pointerEvents="none"
      style={[{ position: 'absolute', left: x - c, top: y - c, width: box, height: box }, style]}
    >
      <Svg width={box} height={box}>
        <Defs>
          <RadialGradient id={id} cx="50%" cy="50%" r="50%">
            <Stop offset="0" stopColor={spark.tint} stopOpacity="0.28" />
            <Stop offset="0.35" stopColor={spark.tint} stopOpacity="0.08" />
            <Stop offset="1" stopColor={spark.tint} stopOpacity="0" />
          </RadialGradient>
        </Defs>
        <Circle cx={c} cy={c} r={c} fill={`url(#${id})`} />
        <G stroke={spark.tint} strokeLinecap="round">
          {/* The long pair is the diffraction cross; the short diagonals are
              what stops it looking like a plus sign. */}
          <Line x1={c - arm} y1={c} x2={c + arm} y2={c} strokeWidth={0.9} strokeOpacity={0.4} />
          <Line x1={c} y1={c - arm} x2={c} y2={c + arm} strokeWidth={0.9} strokeOpacity={0.4} />
          <Line
            x1={c - arm * 0.42}
            y1={c - arm * 0.42}
            x2={c + arm * 0.42}
            y2={c + arm * 0.42}
            strokeWidth={0.7}
            strokeOpacity={0.18}
          />
          <Line
            x1={c + arm * 0.42}
            y1={c - arm * 0.42}
            x2={c - arm * 0.42}
            y2={c + arm * 0.42}
            strokeWidth={0.7}
            strokeOpacity={0.18}
          />
        </G>
        <Circle cx={c} cy={c} r={spark.size * 0.17} fill="#FFFFFF" fillOpacity={0.95} />
      </Svg>
    </Animated.View>
  );
}

// ---------------------------------------------------------------------------
// The band
// ---------------------------------------------------------------------------

/**
 * The band, as stations along a line.
 *
 * `t` runs 0 to 1 from where the band enters the top of the frame to where it
 * leaves the bottom. The core sits low rather than in the middle, for two
 * reasons: the middle is the Moon and would be masked away, and the galactic
 * centre really does sit low from anywhere this app is used.
 *
 * Alternating warm and cool stops. A stripe of one flat tone is the thing that
 * gives a drawn galaxy away.
 */
const BAND: { t: number; r: number; colour: string; peak: number }[] = [
  { t: 0.02, r: 0.52, colour: '#B9B2C8', peak: 0.15 },
  { t: 0.16, r: 0.56, colour: '#C9C0B4', peak: 0.22 },
  { t: 0.30, r: 0.58, colour: '#BDB4C6', peak: 0.26 },
  { t: 0.46, r: 0.60, colour: '#D2C8B8', peak: 0.22 },
  { t: 0.62, r: 0.60, colour: '#BAB2C4', peak: 0.26 },
  { t: 0.78, r: 0.62, colour: '#D8CDBA', peak: 0.32 },
  { t: 0.92, r: 0.54, colour: '#B7B0C6', peak: 0.19 },
];

/** The Great Rift and its cousins — the dust that makes a cloud look deep. */
const LANES: { t: number; across: number; r: number }[] = [
  { t: 0.20, across: 0.18, r: 0.22 },
  { t: 0.37, across: -0.22, r: 0.19 },
  { t: 0.70, across: 0.24, r: 0.24 },
  { t: 0.86, across: -0.16, r: 0.20 },
];

/** Star cloud along the band, so it reads as stars rather than as a smear. */
const CLOUD = (() => {
  const random = seeded(20260902);
  return Array.from({ length: 46 }, () => {
    // Rough gaussian across the band — three uniforms is close enough at this
    // size and costs nothing.
    const across = ((random() + random() + random()) / 3 - 0.5) * 1.5;
    const size = random() ** 3;
    return { t: random(), across, r: 0.8 + size * 2.4, o: 0.35 + random() * 0.55 };
  });
})();

function Galaxy({
  width,
  height,
  scrollY,
}: {
  width: number;
  height: number;
  scrollY: SharedValue<number>;
}) {
  /**
   * Drawn in the hero's own pixels rather than in a percentage box.
   *
   * The first attempt built the band inside an oversized square with a 0–100
   * viewBox and turned it. The mask hole is a circle the size of the Moon, the
   * Moon is most of the screen's width, and in that square the whole visible
   * slice landed inside the hole — a galaxy that was drawn perfectly and
   * appeared nowhere. In pixels a circle is a circle and there is nothing to
   * work back through.
   */
  const at = (t: number, across = 0) => ({
    // The line runs off both ends of the frame, so the band arrives from
    // somewhere rather than starting at the top edge.
    x: width * (-0.18 + 1.36 * t) + across * width,
    y: height * (-0.1 + 1.2 * t),
  });

  const breath = useSharedValue(0.8);

  useEffect(() => {
    breath.value = withRepeat(
      withTiming(1, { duration: 17000, easing: Easing.inOut(Easing.sin) }),
      -1,
      true,
    );
  }, [breath]);

  // Leaves faster than the photograph and slower than the words. Three speeds
  // is what makes a flat screen have a front and a back.
  const style = useAnimatedStyle(() => ({
    opacity:
      breath.value * interpolate(scrollY.value, [0, height * 0.6], [1, 0], Extrapolation.CLAMP),
    transform: [
      { translateY: interpolate(scrollY.value, [0, height], [0, height * 0.1], Extrapolation.CLAMP) },
    ],
  }));

  return (
    <Animated.View pointerEvents="none" style={[StyleSheet.absoluteFill, style]}>
      <Svg width={width} height={height} viewBox={`0 0 ${width} ${height}`}>
        <Defs>
          {BAND.map((glow, index) => {
            const { x, y } = at(glow.t);
            return (
              <RadialGradient
                key={index}
                id={`mw${index}`}
                gradientUnits="userSpaceOnUse"
                cx={x}
                cy={y}
                r={width * glow.r}
              >
                <Stop offset="0" stopColor={glow.colour} stopOpacity={String(glow.peak)} />
                <Stop offset="0.42" stopColor={glow.colour} stopOpacity={String(glow.peak * 0.48)} />
                <Stop offset="1" stopColor={glow.colour} stopOpacity="0" />
              </RadialGradient>
            );
          })}

          {LANES.map((lane, index) => {
            const { x, y } = at(lane.t, lane.across);
            return (
              <RadialGradient
                key={`l${index}`}
                id={`mwl${index}`}
                gradientUnits="userSpaceOnUse"
                cx={x}
                cy={y}
                r={width * lane.r}
              >
                <Stop offset="0" stopColor="#07060F" stopOpacity="0.6" />
                <Stop offset="1" stopColor="#07060F" stopOpacity="0" />
              </RadialGradient>
            );
          })}

          {/* White shows, black hides. The black core is the Moon — the galaxy
              is a hundred thousand light years behind it, so a wash of it lying
              across the disc would be light in front of the nearest thing in
              the sky. */}
          <RadialGradient
            id="mw-hole"
            gradientUnits="userSpaceOnUse"
            cx={width / 2}
            cy={height / 2}
            r={width * 0.66}
          >
            {/* Opaque past the disc's half-height — which is the larger of its
                two half-axes, so a round hole has to clear that one — and gone
                by two thirds of the width. */}
            <Stop offset="0" stopColor="#000000" />
            <Stop offset="0.61" stopColor="#000000" />
            <Stop offset="1" stopColor="#FFFFFF" />
          </RadialGradient>
          <Mask id="mw-mask">
            <Rect x="0" y="0" width={width} height={height} fill="url(#mw-hole)" />
          </Mask>
        </Defs>

        <G mask="url(#mw-mask)">
          {BAND.map((_, index) => (
            <Rect key={index} x="0" y="0" width={width} height={height} fill={`url(#mw${index})`} />
          ))}
          {LANES.map((_, index) => (
            <Rect
              key={`l${index}`}
              x="0"
              y="0"
              width={width}
              height={height}
              fill={`url(#mwl${index})`}
            />
          ))}
          {CLOUD.map((star, index) => {
            const { x, y } = at(star.t, star.across * 0.42);
            return (
              <Circle
                key={`s${index}`}
                cx={x}
                cy={y}
                r={star.r}
                fill="#FFFFFF"
                fillOpacity={star.o}
              />
            );
          })}
        </G>
      </Svg>
    </Animated.View>
  );
}

// ---------------------------------------------------------------------------
// The name
// ---------------------------------------------------------------------------

/**
 * The wordmark, lit letter by letter.
 *
 * There is no gradient-filled text on this platform without a masking library,
 * and one is not worth a dependency for six characters — so each letter simply
 * gets its own colour off the ramp. At six letters and this tracking the eye
 * reads the steps as a gradient anyway, and it buys something a real gradient
 * could not: each letter is its own node, so light can travel along the word.
 *
 * The ramp runs violet to gold: the app's accent at one end, and at the other
 * the warm it uses for the Sun. Cold to warm across the name of a sky app.
 */
const BRAND = [
  { char: 'K', colour: '#9C8CFF' },
  { char: 'O', colour: '#B097FB' },
  { char: 'S', colour: '#CBA3F0' },
  { char: 'M', colour: '#E6AFCE' },
  { char: 'I', colour: '#F2C08F' },
  { char: 'Q', colour: '#F5D27A' },
];

function Brand() {
  const sweep = useSharedValue(0);

  useEffect(() => {
    // Runs one way and restarts: light travels along a sign in one direction.
    // Reversing it would be a pendulum, which is a thing signs do not do.
    sweep.value = withRepeat(
      withTiming(1, { duration: 5200, easing: Easing.inOut(Easing.quad) }),
      -1,
      false,
    );
  }, [sweep]);

  return (
    <View style={styles.brand}>
      {/* The bloom: the same row again, blurred, underneath. Per-letter
          shadows give the tube; this gives the haze around it, which is the
          half people read as neon.

          It has to be the *same shape* — six Texts in a row — and not one Text
          reading "KOSMIQ". Tracking is not applied identically to a string of
          six glyphs and to six strings of one, so the single Text came out
          wider and hung a ghost K off the left of the word and a ghost Q off
          the right. Two rows built the same way cannot disagree. */}
      <View style={[styles.brandRow, styles.brandBloomRow]} pointerEvents="none">
        {BRAND.map((letter, index) => (
          <Text
            key={index}
            style={[styles.brandBloomLetter, { color: letter.colour, textShadowColor: letter.colour }]}
          >
            {letter.char}
          </Text>
        ))}
      </View>
      <View style={styles.brandRow}>
        {BRAND.map((letter, index) => (
          <BrandLetter
            key={index}
            char={letter.char}
            colour={letter.colour}
            at={index / (BRAND.length - 1)}
            sweep={sweep}
          />
        ))}
      </View>
    </View>
  );
}

function BrandLetter({
  char,
  colour,
  at,
  sweep,
}: {
  char: string;
  colour: string;
  /** Where this letter sits along the word, 0 to 1. */
  at: number;
  sweep: SharedValue<number>;
}) {
  const style = useAnimatedStyle(() => {
    // The highlight starts off the left edge and leaves past the right, so the
    // first and last letters get a full pass rather than half of one.
    const head = sweep.value * 1.5 - 0.25;
    const near = Math.max(0, 1 - Math.abs(head - at) / 0.3);
    return {
      color: interpolateColor(near, [0, 1], [colour, '#FFF7E4']),
      opacity: 0.84 + near * 0.16,
    };
  });

  return (
    <Animated.Text style={[styles.brandLetter, { textShadowColor: alpha(colour, 0.85) }, style]}>
      {char}
    </Animated.Text>
  );
}

// ---------------------------------------------------------------------------
// The screen
// ---------------------------------------------------------------------------

export function Welcome({
  height,
  greeting,
  tagline,
  cue,
  scrollY,
  onCue,
}: {
  height: number;
  greeting: string;
  tagline: string;
  cue: string;
  scrollY: SharedValue<number>;
  /** Takes the page down to the grid, for a thumb that would rather tap. */
  onCue: () => void;
}) {
  const { width } = useWindowDimensions();

  const drift = useSharedValue(0);
  const pulse = useSharedValue(0);

  useEffect(() => {
    drift.value = withRepeat(
      withTiming(1, { duration: 26000, easing: Easing.inOut(Easing.sin) }),
      -1,
      true,
    );
    pulse.value = withRepeat(
      withTiming(1, { duration: 4200, easing: Easing.inOut(Easing.sin) }),
      -1,
      true,
    );
  }, [drift, pulse]);

  // The photograph leaves slowest of the three layers, and swells by four per
  // cent over almost half a minute — under the threshold where an eye catches
  // the turn and calls it a loop.
  const photo = useAnimatedStyle(() => ({
    transform: [
      { scale: 1 + drift.value * 0.04 },
      { translateY: interpolate(scrollY.value, [0, height], [0, height * 0.06], Extrapolation.CLAMP) },
    ],
  }));

  // Words go first and go furthest, because they are the thing in the way.
  const body = useAnimatedStyle(() => ({
    opacity: interpolate(scrollY.value, [0, height * 0.42], [1, 0], Extrapolation.CLAMP),
    transform: [
      { translateY: interpolate(scrollY.value, [0, height], [0, height * 0.24], Extrapolation.CLAMP) },
    ],
  }));

  // The haze behind the greeting, breathing on its own clock. A neon sign that
  // holds perfectly still is a printed one.
  // Kept low on purpose. At full strength the blurred copy's letterforms
  // merge into each other and the word ends up in a lit white box — a
  // highlighter pen rather than a sign.
  const halo = useAnimatedStyle(() => ({ opacity: 0.16 + pulse.value * 0.26 }));

  // The cue's whole job is to say the page moves. The first flick says it
  // better, so it leaves as soon as one happens.
  const hint = useAnimatedStyle(() => ({
    opacity: interpolate(scrollY.value, [0, 40], [1, 0], Extrapolation.CLAMP),
  }));

  return (
    <View style={[styles.hero, { height }]}>
      <Sky width={width} height={height} scrollY={scrollY} />

      <Animated.View style={[StyleSheet.absoluteFill, styles.moonLayer, photo]} pointerEvents="none">
        <Image
          source={MOON}
          style={{ width: width * MOON_WIDTH, height: width * MOON_WIDTH * MOON_ASPECT }}
          resizeMode="contain"
        />
      </Animated.View>

      <Galaxy width={width} height={height} scrollY={scrollY} />

      {/* Dark at both ends and clear through the middle: the words sit on the
          top of the frame and the button on the bottom of it, and neither is
          allowed to depend on the photograph happening to be black there. */}
      <LinearGradient
        colors={[
          alpha(colors.bg, 0.72),
          alpha(colors.bg, 0.2),
          alpha(colors.bg, 0.02),
          alpha(colors.bg, 0.4),
        ]}
        locations={[0, 0.24, 0.66, 1]}
        style={StyleSheet.absoluteFill}
        pointerEvents="none"
      />

      <Animated.View style={[styles.body, body]} pointerEvents="none">
        <Brand />
        <View style={styles.words}>
          <View>
            {/* Two copies of one string: a wide soft one for the glow and a
                clean one for the reading. One Text cannot do both — a shadow
                broad enough to bloom takes the letterforms with it. */}
            <Animated.Text style={[styles.greetingHalo, halo]}>{greeting}</Animated.Text>
            <Text style={styles.greeting}>{greeting}</Text>
          </View>
          <LinearGradient
            colors={['transparent', alpha(colors.accentSoft, 0.75), 'transparent']}
            start={{ x: 0, y: 0.5 }}
            end={{ x: 1, y: 0.5 }}
            style={styles.rule}
          />
          <Text style={styles.tagline}>{tagline}</Text>
        </View>
      </Animated.View>

      <Animated.View style={[styles.cue, hint]}>
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={cue}
          onPress={onCue}
          style={({ pressed }) => [styles.cueTap, pressed && styles.cuePressed]}
        >
          <Text style={styles.cueText}>{cue}</Text>
          <View style={styles.cueRing}>
            <Chevron />
          </View>
        </Pressable>
      </Animated.View>
    </View>
  );
}

/** Drawn, and nudging downward on its own — the direction is the message. */
function Chevron() {
  const v = useSharedValue(0);

  useEffect(() => {
    v.value = withRepeat(
      withTiming(1, { duration: 1400, easing: Easing.inOut(Easing.quad) }),
      -1,
      true,
    );
  }, [v]);

  const style = useAnimatedStyle(() => ({
    transform: [{ translateY: v.value * 5 }],
    opacity: 0.55 + v.value * 0.45,
  }));

  return (
    <Animated.View style={style}>
      <Svg width={26} height={16} viewBox="0 0 26 16" fill="none">
        <G stroke={colors.accentSoft} strokeWidth={2.3} strokeLinecap="round">
          <Line x1={2.6} y1={3} x2={13} y2={12.6} />
          <Line x1={23.4} y1={3} x2={13} y2={12.6} />
        </G>
      </Svg>
    </Animated.View>
  );
}

const BRAND_TYPE = {
  fontSize: 13,
  fontWeight: '700' as const,
  letterSpacing: 6.5,
  textAlign: 'center' as const,
};

const styles = StyleSheet.create({
  hero: { alignItems: 'center', overflow: 'hidden' },
  moonLayer: { alignItems: 'center', justifyContent: 'center' },

  // The words live at the top of the frame; the Moon has the middle.
  body: { alignSelf: 'stretch', alignItems: 'center', paddingTop: space.xl, gap: space.lg },

  brand: { alignItems: 'center', justifyContent: 'center' },
  brandRow: { flexDirection: 'row' },
  brandLetter: {
    ...BRAND_TYPE,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 13,
  },
  brandBloomRow: { position: 'absolute', left: 0, right: 0, top: 0, justifyContent: 'center' },
  brandBloomLetter: {
    ...BRAND_TYPE,
    opacity: 0.45,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 24,
  },

  words: { alignItems: 'center', gap: space.md, paddingHorizontal: space.lg },
  greeting: {
    ...type.display,
    color: colors.text,
    textAlign: 'center',
    textShadowColor: alpha(colors.accentSoft, 0.55),
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 14,
  },
  greetingHalo: {
    ...type.display,
    position: 'absolute',
    left: 0,
    right: 0,
    top: 0,
    // The saturated accent rather than the pale one. A neon sign is a white
    // core in a coloured haze; a pale haze behind white letters is just fog.
    color: colors.accent,
    textAlign: 'center',
    textShadowColor: colors.accent,
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 20,
  },
  // A lit hairline, so the name and the sentence read as two things rather
  // than as one paragraph with a gap in it.
  rule: { width: 132, height: 1, borderRadius: radius.pill },
  tagline: {
    ...type.body,
    color: '#C6BEE6',
    textAlign: 'center',
    lineHeight: 22,
    maxWidth: 300,
    textShadowColor: alpha(colors.accent, 0.45),
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },

  // Lifted well clear of the gesture bar, where a control at the very bottom
  // edge competes with the system's own.
  cue: { position: 'absolute', bottom: space.xxl + space.md, alignItems: 'center' },
  cueTap: {
    alignItems: 'center',
    gap: space.sm,
    paddingHorizontal: space.lg,
    paddingVertical: space.sm,
  },
  cuePressed: { opacity: 0.6 },
  cueText: {
    ...type.label,
    fontSize: 11,
    color: colors.accentSoft,
    letterSpacing: 2.4,
    textShadowColor: alpha(colors.accent, 0.6),
    textShadowOffset: { width: 0, height: 0 },
    textShadowRadius: 10,
  },
  // A ring, so it reads as something to press rather than as an arrow lying on
  // the page — which is what it is: tapping it goes to the grid.
  cueRing: {
    width: 52,
    height: 52,
    borderRadius: radius.pill,
    borderWidth: 1,
    borderColor: alpha(colors.accentSoft, 0.5),
    backgroundColor: colors.glass,
    boxShadow: `0 0 20px ${alpha(colors.accent, 0.4)}`,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

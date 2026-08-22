/**
 * North Indian (diamond) kundli chart.
 *
 * The layout is fixed: house 1 always sits top-centre and the houses run
 * anticlockwise from it, with the rashi *number* printed in each house rather
 * than the house number. That is what makes a North Indian chart readable to
 * someone who grew up with one — the shape never moves, only the numbers do.
 *
 * Geometry: a square, both diagonals, and the diamond joining the four edge
 * midpoints. Those six lines cut the square into exactly twelve regions — four
 * rhombi inside the diamond (houses 1, 4, 7, 10) and eight corner triangles.
 *
 * `HOUSES` below is the single source of that geometry. The label positions are
 * *derived* from it as centroids rather than written out a second time, which
 * is the whole reason it is a table: a hand-written anchor and the cell it
 * belongs to can drift apart silently, and a number printed in the wrong house
 * is the one error in this component nobody would catch by looking.
 *
 * --- How it is drawn ------------------------------------------------------
 *
 * A pane of glass, like every other card in this app. The background is a
 * translucent gradient rather than a flat fill, so the star field behind the
 * screen still shows through — the chart used to be the one opaque rectangle in
 * a design made entirely of glass, and it sat on top of the app instead of in
 * it.
 *
 * Each house is lit from its own centre by a radial gradient in its rashi's
 * element. Flat tints were tried first and went muddy: a low alpha of anything
 * over this violet ground turns to silt, and twelve flat blocks read as
 * twelve blocks. Light fades, so it stays light.
 *
 * The square sits inside a mat with a hairline out at the edge — the double
 * border a printed kundli has. It also buys the margin that keeps a graha in a
 * corner triangle from touching the frame.
 *
 * --- What the colour says -------------------------------------------------
 *
 * Three things, each on top of a label rather than instead of one:
 *
 * - **A wash per house** for the rashi's element. The twelve rashis cycle fire,
 *   earth, air, water in order, so this is `index % 4` — a fact, not a lookup.
 * - **A colour per graha**, so the same body is the same colour everywhere. The
 *   graha list on the chart screen repeats these as dots, which is what makes
 *   this a legend rather than decoration.
 * - **Combust grahas are drawn dim.** That is what combustion is: a planet lost
 *   in the Sun's glare. Encoding it as brightness rather than as a third colour
 *   leaves hue free to mean identity, and lets a graha that is both combust and
 *   retrograde show both at once — which the old chart could not, because
 *   colour was carrying both states and only one of them could win.
 */

import { useId, useState } from 'react';
import { StyleSheet, View } from 'react-native';
import Svg, {
  Defs,
  G,
  Line,
  LinearGradient,
  Polygon,
  RadialGradient,
  Rect,
  Stop,
  TSpan,
  Text as SvgText,
} from 'react-native-svg';

import { colors, elementGlow, elementInk, grahaColour } from '../theme';
import type { Chart } from '../api/types';

const RASHI_ORDER = [
  'Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha', 'Kanya',
  'Tula', 'Vrishchika', 'Dhanu', 'Makara', 'Kumbha', 'Meena',
];

/** Mesha is fire, Vrishabha earth, Mithuna air, Karka water — then it repeats. */
const ELEMENTS = ['fire', 'earth', 'air', 'water'] as const;

const GRAHA_ABBR: Record<string, string> = {
  Sun: 'Su',
  Moon: 'Mo',
  Mars: 'Ma',
  Mercury: 'Me',
  Jupiter: 'Ju',
  Venus: 'Ve',
  Saturn: 'Sa',
  Rahu: 'Ra',
  Ketu: 'Ke',
};

/** Hairlines, as a share of the accent's own violet. */
const LATTICE = 'rgba(185, 174, 255, 0.22)';
const DIAMOND = 'rgba(185, 174, 255, 0.30)';
const FRAME = 'rgba(185, 174, 255, 0.32)';
const FRAME_OUTER = 'rgba(185, 174, 255, 0.15)';

/** The mat between the outer hairline and the chart square, as a share of it. */
const MAT = 0.038;

type Point = readonly [number, number];

/**
 * The twelve cells, as fractions of the chart square.
 *
 * Vertices go round each cell in order. Every rhombus here is a parallelogram
 * and every other cell a triangle, so the plain average of the vertices is the
 * true centroid in both cases — which is what `centreOf` relies on.
 */
const HOUSES: Record<number, readonly Point[]> = {
  1: [[1 / 2, 0], [1 / 4, 1 / 4], [1 / 2, 1 / 2], [3 / 4, 1 / 4]],
  2: [[0, 0], [1 / 2, 0], [1 / 4, 1 / 4]],
  3: [[0, 0], [1 / 4, 1 / 4], [0, 1 / 2]],
  4: [[0, 1 / 2], [1 / 4, 1 / 4], [1 / 2, 1 / 2], [1 / 4, 3 / 4]],
  5: [[0, 1], [0, 1 / 2], [1 / 4, 3 / 4]],
  6: [[0, 1], [1 / 4, 3 / 4], [1 / 2, 1]],
  7: [[1 / 2, 1], [1 / 4, 3 / 4], [1 / 2, 1 / 2], [3 / 4, 3 / 4]],
  8: [[1, 1], [1 / 2, 1], [3 / 4, 3 / 4]],
  9: [[1, 1], [3 / 4, 3 / 4], [1, 1 / 2]],
  10: [[1, 1 / 2], [3 / 4, 1 / 4], [1 / 2, 1 / 2], [3 / 4, 3 / 4]],
  11: [[1, 0], [1, 1 / 2], [3 / 4, 1 / 4]],
  12: [[1, 0], [3 / 4, 1 / 4], [1 / 2, 0]],
};

const HOUSE_NUMBERS = Object.keys(HOUSES).map(Number);

function centreOf(cell: readonly Point[]): Point {
  const x = cell.reduce((sum, [px]) => sum + px, 0) / cell.length;
  const y = cell.reduce((sum, [, py]) => sum + py, 0) / cell.length;
  return [x, y];
}

/** Distance from the centroid to the furthest vertex — the glow's reach. */
function reachOf(cell: readonly Point[]): number {
  const [cx, cy] = centreOf(cell);
  return Math.max(...cell.map(([x, y]) => Math.hypot(x - cx, y - cy)));
}

/**
 * Whether ℞ is worth printing.
 *
 * The nodes are computed as the mean node and so are retrograde *always* — the
 * engine has a test saying exactly that. Marking them is not wrong, it is
 * empty: a flag that never varies carries no information, and in a corner
 * triangle holding five grahas it costs the room a real one needs.
 *
 * The mark itself is a raised R rather than ℞ (U+211E). That character is not
 * in Android's default font, so on a real device it fell back to a glyph that
 * rendered as a mangled Ŗ — caught by running this on a phone, and invisible in
 * every desktop preview.
 */
function marksRetrograde(graha: { graha: string; retrograde: boolean }): boolean {
  return graha.retrograde && graha.graha !== 'Rahu' && graha.graha !== 'Ketu';
}

export function KundliChart({ chart, size }: { chart: Chart; size?: number }) {
  // Measured rather than assumed when the caller does not say. The old default
  // was a flat 320, which is wider than a 360dp phone leaves after the screen's
  // own padding — the chart ran off the right edge on the narrowest devices
  // this app supports.
  const [measured, setMeasured] = useState(0);
  const total = size ?? measured;

  // Gradients are referenced by id, and two charts on one screen would
  // otherwise both define `#g1` and both resolve to whichever mounted last.
  const uid = useId().replace(/[^a-zA-Z0-9]/g, '');

  const grahasByHouse = new Map<number, typeof chart.grahas>();
  for (const graha of chart.grahas) {
    const list = grahasByHouse.get(graha.house) ?? [];
    list.push(graha);
    grahasByHouse.set(graha.house, list);
  }

  const mat = total * MAT;
  const side = total - 2 * mat;
  /** Fraction of the chart square → absolute coordinate inside the mat. */
  const at = (v: number) => mat + v * side;
  const points = (cell: readonly Point[]) =>
    cell.map(([x, y]) => `${at(x)},${at(y)}`).join(' ');

  const elementOf = (house: number) => {
    const index = RASHI_ORDER.indexOf(chart.houses[String(house)]);
    return index >= 0 ? { index, element: ELEMENTS[index % 4] } : null;
  };

  return (
    <View
      style={styles.wrap}
      onLayout={(event) => setMeasured(Math.floor(event.nativeEvent.layout.width))}
    >
      {total > 0 ? (
        <Svg width={total} height={total} viewBox={`0 0 ${total} ${total}`}>
          <Defs>
            <LinearGradient id={`${uid}-bg`} x1="0" y1="0" x2="0.9" y2="1">
              <Stop offset="0" stopColor="#2E2858" stopOpacity="0.84" />
              <Stop offset="0.5" stopColor="#1C1934" stopOpacity="0.87" />
              <Stop offset="1" stopColor="#191630" stopOpacity="0.90" />
            </LinearGradient>

            {HOUSE_NUMBERS.map((house) => {
              const found = elementOf(house);
              if (!found) return null;
              const cell = HOUSES[house];
              const [cx, cy] = centreOf(cell);
              const glow = elementGlow[found.element];
              return (
                <RadialGradient
                  key={house}
                  id={`${uid}-h${house}`}
                  gradientUnits="userSpaceOnUse"
                  cx={at(cx)}
                  cy={at(cy)}
                  r={reachOf(cell) * side}
                >
                  <Stop offset="0" stopColor={glow} stopOpacity="0.19" />
                  <Stop offset="1" stopColor={glow} stopOpacity="0.065" />
                </RadialGradient>
              );
            })}

            <RadialGradient
              id={`${uid}-lagna`}
              gradientUnits="userSpaceOnUse"
              cx={at(centreOf(HOUSES[1])[0])}
              cy={at(centreOf(HOUSES[1])[1])}
              r={reachOf(HOUSES[1]) * side}
            >
              <Stop offset="0" stopColor={colors.accentSoft} stopOpacity="0.24" />
              <Stop offset="1" stopColor={colors.accent} stopOpacity="0.07" />
            </RadialGradient>
          </Defs>

          <Rect x={0} y={0} width={total} height={total} fill={`url(#${uid}-bg)`} />

          {HOUSE_NUMBERS.map((house) =>
            elementOf(house) ? (
              <Polygon
                key={`glow-${house}`}
                points={points(HOUSES[house])}
                fill={`url(#${uid}-h${house})`}
              />
            ) : null,
          )}

          {/* Lagna. House 1 is always the ascendant in this layout, so this is
              not a highlight that moves — it is where the eye should start. */}
          <Polygon points={points(HOUSES[1])} fill={`url(#${uid}-lagna)`} />

          <G stroke={LATTICE} strokeWidth={1} fill="none">
            <Line x1={at(0)} y1={at(0)} x2={at(1)} y2={at(1)} />
            <Line x1={at(1)} y1={at(0)} x2={at(0)} y2={at(1)} />
          </G>

          {/* A touch brighter than the diagonals: the diamond is the chart's
              spine, and the four rhombi read as cells because of it. */}
          <Polygon
            points={`${at(0.5)},${at(0)} ${at(1)},${at(0.5)} ${at(0.5)},${at(1)} ${at(0)},${at(0.5)}`}
            fill="none"
            stroke={DIAMOND}
            strokeWidth={1}
          />

          {/* After the lattice, not before: drawn first, the grey lines land on
              top of it and leave a doubled edge along every side of the
              diamond. */}
          <Polygon
            points={points(HOUSES[1])}
            fill="none"
            stroke={colors.accentSoft}
            strokeOpacity={0.8}
            strokeWidth={1.25}
          />

          {/* The double border a printed kundli has: the chart square, and a
              hairline out at the edge of the mat. */}
          <Rect x={mat} y={mat} width={side} height={side} fill="none" stroke={FRAME} strokeWidth={1.25} />
          <Rect
            x={0.5}
            y={0.5}
            width={total - 1}
            height={total - 1}
            fill="none"
            stroke={FRAME_OUTER}
            strokeWidth={1}
          />

          {HOUSE_NUMBERS.map((house) => {
            const found = elementOf(house);
            const occupants = grahasByHouse.get(house) ?? [];

            const [fx, fy] = centreOf(HOUSES[house]);
            const cx = at(fx);
            const cy = at(fy);

            // Scaled off the chart's own width so the type stays in proportion
            // at any size, then rounded to whole points: a 10.4px glyph is
            // rendered blurry by the text rasteriser on both platforms.
            const unit = side / 320;
            const crowded = occupants.length > 4;
            const glyph = Math.max(8, Math.round((crowded ? 9 : 11) * unit));
            const numberSize = Math.max(7, Math.round(10 * unit));

            // Two columns once a house holds more than three. A corner triangle
            // is only a quarter of the side tall, and a stellium stacked one
            // per line used to run out through the edge of the chart.
            const perRow = occupants.length > 3 ? 2 : 1;
            const rows = Math.ceil(occupants.length / perRow);

            const line = glyph + 2 * unit;
            const numberLine = numberSize + 3 * unit;
            const top = cy - (numberLine + rows * line) / 2;

            // 0.78 of the way down its own row puts a baseline where the glyph
            // looks vertically centred in it.
            const baselineOf = (row: number) => top + numberLine + (row + 0.78) * line;

            return (
              <G key={`text-${house}`}>
                <SvgText
                  x={cx}
                  y={top + numberLine * 0.78}
                  fill={found ? elementInk[found.element] : colors.textFaint}
                  fillOpacity={0.95}
                  fontSize={numberSize}
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {found ? String(found.index + 1) : ''}
                </SvgText>

                {Array.from({ length: rows }, (_, row) => {
                  const inRow = occupants.slice(row * perRow, row * perRow + perRow);
                  const gap = glyph * 2.4;
                  return inRow.map((graha, column) => (
                    <SvgText
                      key={graha.graha}
                      x={cx + (column - (inRow.length - 1) / 2) * gap}
                      y={baselineOf(row)}
                      fill={grahaColour[graha.graha] ?? colors.text}
                      // Burnt by the Sun, so drawn as if seen through its glare.
                      opacity={graha.combust ? 0.55 : 1}
                      fontSize={glyph}
                      fontWeight="700"
                      textAnchor="middle"
                    >
                      {GRAHA_ABBR[graha.graha] ?? graha.graha.slice(0, 2)}
                      {marksRetrograde(graha) ? (
                        <TSpan
                          fontSize={Math.max(7, Math.round(glyph * 0.72))}
                          dx={glyph * 0.1}
                          dy={-glyph * 0.3}
                        >
                          R
                        </TSpan>
                      ) : null}
                    </SvgText>
                  ));
                })}
              </G>
            );
          })}
        </Svg>
      ) : null}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { width: '100%', aspectRatio: 1, alignItems: 'center', justifyContent: 'center' },
});

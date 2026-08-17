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
 */

import { StyleSheet, View } from 'react-native';
import Svg, { G, Line, Polygon, Rect, Text as SvgText } from 'react-native-svg';

import { colors } from '../theme';
import type { Chart } from '../api/types';

const RASHI_ORDER = [
  'Mesha', 'Vrishabha', 'Mithuna', 'Karka', 'Simha', 'Kanya',
  'Tula', 'Vrishchika', 'Dhanu', 'Makara', 'Kumbha', 'Meena',
];

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

/** Text anchor for each house, as a fraction of the chart's side. */
const HOUSE_ANCHORS: Record<number, { x: number; y: number }> = {
  1: { x: 1 / 2, y: 1 / 4 },
  2: { x: 1 / 4, y: 1 / 12 },
  3: { x: 1 / 12, y: 1 / 4 },
  4: { x: 1 / 4, y: 1 / 2 },
  5: { x: 1 / 12, y: 3 / 4 },
  6: { x: 1 / 4, y: 11 / 12 },
  7: { x: 1 / 2, y: 3 / 4 },
  8: { x: 3 / 4, y: 11 / 12 },
  9: { x: 11 / 12, y: 3 / 4 },
  10: { x: 3 / 4, y: 1 / 2 },
  11: { x: 11 / 12, y: 1 / 4 },
  12: { x: 3 / 4, y: 1 / 12 },
};

export function KundliChart({ chart, size = 320 }: { chart: Chart; size?: number }) {
  const s = size;
  const h = s / 2;
  const q = s / 4;
  const t = (3 * s) / 4;

  const grahasByHouse = new Map<number, typeof chart.grahas>();
  for (const graha of chart.grahas) {
    const list = grahasByHouse.get(graha.house) ?? [];
    list.push(graha);
    grahasByHouse.set(graha.house, list);
  }

  return (
    <View style={styles.wrap}>
      <Svg width={s} height={s} viewBox={`0 0 ${s} ${s}`}>
        <Rect x={0} y={0} width={s} height={s} fill={colors.surface} />

        {/* Lagna sits in house 1 — tint it so the eye lands there first. */}
        <Polygon
          points={`${h},0 ${q},${q} ${h},${h} ${t},${q}`}
          fill={colors.accentDim}
        />

        <G stroke={colors.border} strokeWidth={1}>
          <Rect x={0.5} y={0.5} width={s - 1} height={s - 1} fill="none" />
          {/* Diagonals. */}
          <Line x1={0} y1={0} x2={s} y2={s} />
          <Line x1={s} y1={0} x2={0} y2={s} />
          {/* Diamond through the edge midpoints. */}
          <Line x1={h} y1={0} x2={s} y2={h} />
          <Line x1={s} y1={h} x2={h} y2={s} />
          <Line x1={h} y1={s} x2={0} y2={h} />
          <Line x1={0} y1={h} x2={h} y2={0} />
        </G>

        {Object.entries(HOUSE_ANCHORS).map(([key, anchor]) => {
          const house = Number(key);
          const rashiName = chart.houses[String(house)];
          const rashiNumber = RASHI_ORDER.indexOf(rashiName) + 1;
          const occupants = grahasByHouse.get(house) ?? [];

          const cx = anchor.x * s;
          const cy = anchor.y * s;

          // Stack occupants under the rashi number, centred on the anchor.
          const lineHeight = 12;
          const startY = cy - ((occupants.length - 1) * lineHeight) / 2 + 5;

          return (
            <G key={house}>
              <SvgText
                x={cx}
                y={cy - (occupants.length > 0 ? 14 : 0)}
                fill={colors.textFaint}
                fontSize={10}
                fontWeight="600"
                textAnchor="middle"
              >
                {rashiNumber > 0 ? String(rashiNumber) : ''}
              </SvgText>

              {occupants.map((graha, index) => (
                <SvgText
                  key={graha.graha}
                  x={cx}
                  y={startY + index * lineHeight}
                  fill={
                    graha.combust
                      ? colors.combust
                      : graha.retrograde
                        ? colors.retro
                        : colors.text
                  }
                  fontSize={11}
                  fontWeight="700"
                  textAnchor="middle"
                >
                  {GRAHA_ABBR[graha.graha] ?? graha.graha.slice(0, 2)}
                  {graha.retrograde ? ' ℞' : ''}
                </SvgText>
              ))}
            </G>
          );
        })}
      </Svg>
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { alignItems: 'center', justifyContent: 'center' },
});

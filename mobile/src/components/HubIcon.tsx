/**
 * The home cards' line art.
 *
 * Drawn rather than typed, for the reason the sidebar's power glyph exists: the
 * stock Android font is missing enough symbols that a character picked for its
 * looks can ship as an empty box on somebody's phone. A path cannot.
 *
 * Each icon is stroked twice — a thick, nearly transparent pass under a crisp
 * one — which is the whole neon effect. It costs one extra path per icon and
 * needs no shadow API, so it looks the same on every renderer rather than
 * quietly flattening on one of them.
 */

import { ReactNode } from 'react';
import Svg, { Circle, G, Path, Rect } from 'react-native-svg';

import type { HubKey } from '../i18n';

/** Every shape is authored in one 24×24 box so the strokes stay even. */
const SHAPES: Record<HubKey, ReactNode> = {
  today: (
    <>
      <Circle cx={12} cy={12} r={4.4} />
      <Path d="M12 2.4V4.8M12 19.2v2.4M2.4 12h2.4M19.2 12h2.4M5.2 5.2l1.7 1.7M17.1 17.1l1.7 1.7M18.8 5.2l-1.7 1.7M6.9 17.1l-1.7 1.7" />
    </>
  ),
  // Two crossed triangles — the shatkona, which is what the chart screen's
  // north-Indian square is built out of.
  chart: (
    <>
      <Path d="M12 2.8 20.1 16.8 3.9 16.8 Z" />
      <Path d="M12 21.2 3.9 7.2 20.1 7.2 Z" />
    </>
  ),
  matching: (
    <>
      <Path d="M10.4 20.2C10.4 20.2 3 15.4 3 10.5A3.9 3.9 0 0 1 10.4 8.6 3.9 3.9 0 0 1 17.8 10.5C17.8 15.4 10.4 20.2 10.4 20.2Z" />
      <Path d="M16.4 16.6C19.2 14.2 21 11.9 21 9.4A3.3 3.3 0 0 0 16.6 6.3" />
    </>
  ),
  tarot: (
    <>
      <Rect x={3.2} y={5.6} width={9.6} height={13.4} rx={1.6} />
      <Path d="M14.6 5.1 19.9 6.6a1.6 1.6 0 0 1 1.1 2l-3 10.6" />
      <Path d="M8 9.4 8.9 11.7 11.2 12.6 8.9 13.5 8 15.8 7.1 13.5 4.8 12.6 7.1 11.7 Z" />
    </>
  ),
  chat: (
    <>
      <Path d="M4 5.4h16a1.4 1.4 0 0 1 1.4 1.4v8.4a1.4 1.4 0 0 1-1.4 1.4H10.6L6 20.4v-3.8H4a1.4 1.4 0 0 1-1.4-1.4V6.8A1.4 1.4 0 0 1 4 5.4Z" />
      <Path d="M8.2 11h.01M12 11h.01M15.8 11h.01" />
    </>
  ),
  learn: (
    <>
      <Path d="M12 6.6C10.3 5.2 8.2 4.6 4.4 4.6a0.9 0.9 0 0 0-0.9 0.9v12a0.9 0.9 0 0 0 0.9 0.9c3.8 0 5.9 0.6 7.6 2 1.7-1.4 3.8-2 7.6-2a0.9 0.9 0 0 0 0.9-0.9v-12a0.9 0.9 0 0 0-0.9-0.9c-3.8 0-5.9 0.6-7.6 2Z" />
      <Path d="M12 6.6v13.8" />
    </>
  ),
  // A crown, for the one screen that costs something.
  plans: (
    <>
      <Path d="M3.6 8.2 6.9 12.2 12 5.6 17.1 12.2 20.4 8.2 18.8 18.2H5.2Z" />
      <Path d="M5.2 21.2h13.6" />
    </>
  ),
  history: (
    <>
      <Circle cx={12} cy={12.4} r={8.2} />
      <Path d="M12 7.6v4.8l3.2 2" />
      <Path d="M3.8 12.4 6.2 9.9 8.6 12.4" />
    </>
  ),
  settings: (
    <>
      <Circle cx={12} cy={12} r={3.4} />
      <Path d="M12 2.6v3M12 18.4v3M2.6 12h3M18.4 12h3M5.3 5.3l2.1 2.1M16.6 16.6l2.1 2.1M18.7 5.3l-2.1 2.1M7.4 16.6l-2.1 2.1" />
    </>
  ),
};

export function HubIcon({
  name,
  tint,
  size = 40,
}: {
  name: HubKey;
  tint: string;
  size?: number;
}) {
  const shape = SHAPES[name];
  return (
    <Svg width={size} height={size} viewBox="0 0 24 24" fill="none">
      {/* The bloom. Wide and faint, so it reads as light around the line
          rather than as a second, fatter line. */}
      <G
        stroke={tint}
        strokeWidth={4.4}
        strokeLinecap="round"
        strokeLinejoin="round"
        opacity={0.16}
      >
        {shape}
      </G>
      <G stroke={tint} strokeWidth={1.7} strokeLinecap="round" strokeLinejoin="round">
        {shape}
      </G>
    </Svg>
  );
}

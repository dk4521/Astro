/**
 * Placeholder portraits for the chat companions.
 *
 * Drawn rather than shipped or fetched. A remote avatar service would make the
 * first screen of the chat depend on someone else's uptime and on the phone
 * being online; bundled photographs of real people would be a licensing
 * question the app does not need to answer yet. These are obviously
 * illustrations, which is the honest thing for a placeholder to look like —
 * swap `Portrait` for an <Image> when the real art exists and nothing else has
 * to change.
 *
 * Fifteen faces from one drawing: skin, hair colour, clothes and background are
 * parameters, and the hairstyle picks which of a dozen paths to draw. Fifteen
 * hand-written SVGs would have drifted apart the first time an eye moved.
 */

import Svg, {
  Circle,
  ClipPath,
  Defs,
  Ellipse,
  G,
  Path,
  Rect,
} from 'react-native-svg';

type HairStyle =
  | 'long'
  | 'bob'
  | 'bun'
  | 'ponytail'
  | 'braid'
  | 'curly'
  | 'short'
  | 'crop'
  | 'parted'
  | 'wavy';

export type Persona = {
  id: string;
  name: string;
  skin: number;
  hair: number;
  clothes: number;
  bg: number;
  style: HairStyle;
  facial?: 'beard' | 'stubble' | 'moustache';
  /** Head shape. Two faces with the same hair still read as two people. */
  build?: 'round' | 'long';
};

const SKINS = [
  { skin: '#EBC9A6', shade: '#D3AE87' },
  { skin: '#DCA77E', shade: '#C3906A' },
  { skin: '#C98F63', shade: '#B07C54' },
  { skin: '#AC7550', shade: '#946241' },
  { skin: '#8B5C3B', shade: '#764B2E' },
];

const HAIRS = ['#1B1412', '#241C18', '#3A2418', '#4C3020', '#0F0C0B'];

const CLOTHES = [
  '#3E3670', '#5A3160', '#33436E', '#6B3D55', '#2F5A63',
  '#6A4A2E', '#474070', '#2B5560', '#5E3448', '#37504A',
];

const BGS = [
  '#2A2450', '#3A2444', '#25304F', '#402A3E', '#233F4A',
  '#42283A', '#2E2A56', '#1F3346', '#3C2A2A', '#263A38',
];

/**
 * Ten women and five men.
 *
 * The combinations are set out by hand rather than generated: a random mix
 * produced two near-identical faces side by side often enough that picking one
 * became guesswork.
 */
export const PERSONAS: Persona[] = [
  { id: 'meera', name: 'Meera', skin: 1, hair: 0, clothes: 1, bg: 3, style: 'long' },
  { id: 'anaya', name: 'Anaya', skin: 0, hair: 2, clothes: 3, bg: 5, style: 'bun' , build: 'round' },
  { id: 'priya', name: 'Priya', skin: 2, hair: 1, clothes: 4, bg: 4, style: 'ponytail' , build: 'long' },
  { id: 'kavya', name: 'Kavya', skin: 3, hair: 0, clothes: 8, bg: 8, style: 'braid' },
  { id: 'ishita', name: 'Ishita', skin: 0, hair: 3, clothes: 6, bg: 6, style: 'bob' , build: 'round' },
  { id: 'riya', name: 'Riya', skin: 1, hair: 4, clothes: 0, bg: 0, style: 'curly' , build: 'long' },
  { id: 'nisha', name: 'Nisha', skin: 4, hair: 0, clothes: 9, bg: 9, style: 'long' , build: 'long' },
  { id: 'tara', name: 'Tara', skin: 2, hair: 2, clothes: 7, bg: 7, style: 'bun' },
  { id: 'aditi', name: 'Aditi', skin: 3, hair: 1, clothes: 5, bg: 2, style: 'bob' , build: 'round' },
  { id: 'sanya', name: 'Sanya', skin: 1, hair: 3, clothes: 2, bg: 1, style: 'ponytail' },

  { id: 'aarav', name: 'Aarav', skin: 2, hair: 0, clothes: 0, bg: 0, style: 'short' , build: 'round' },
  { id: 'kabir', name: 'Kabir', skin: 3, hair: 4, clothes: 2, bg: 2, style: 'crop', facial: 'beard' , build: 'long' },
  { id: 'rohan', name: 'Rohan', skin: 1, hair: 1, clothes: 6, bg: 6, style: 'parted' },
  { id: 'vikram', name: 'Vikram', skin: 4, hair: 0, clothes: 7, bg: 7, style: 'short', facial: 'moustache' , build: 'round' },
  { id: 'arjun', name: 'Arjun', skin: 0, hair: 2, clothes: 5, bg: 5, style: 'wavy', facial: 'stubble' , build: 'long' },
];

/** The head is an ellipse centred at (50, 46) spanning y 20 to 72. */
const CAP_FULL = 'M27 44 q3 -25 23 -25 q20 0 23 25 q-8 -13 -23 -12 q-15 1 -23 12 z';
const CAP_SHORT = 'M28 42 q2 -22 22 -22 q20 0 22 22 q-6 -12 -22 -11 q-16 1 -22 11 z';
const CAP_CROP = 'M29 41 q2 -20 21 -20 q19 0 21 20 q-6 -10 -21 -9.5 q-15 0.5 -21 9.5 z';
/** Fuller, with a lower hairline and a scalloped edge. */
const CAP_WAVY =
  'M27 45 q1 -25 23 -25 q22 0 23 25 q-4 -6 -8 -8 q-5 4 -9 0 q-5 4 -10 0 q-5 4 -9 0 q-5 2 -10 8 z';

/** Everything drawn behind the head: length, volume, a plait, a tail. */
function HairBack({ style, hair }: { style: HairStyle; hair: string }) {
  switch (style) {
    case 'long':
      return <Path d="M22 44 q0 -30 28 -30 q28 0 28 30 l4 46 q-32 8 -64 0 z" fill={hair} />;
    case 'bob':
      return <Path d="M23 46 q0 -29 27 -29 q27 0 27 29 l2 24 q-29 7 -58 0 z" fill={hair} />;
    case 'bun':
      return (
        <G>
          <Path d="M25 47 q0 -28 25 -28 q25 0 25 28 l2 30 q-27 7 -54 0 z" fill={hair} />
          <Circle cx={50} cy={19} r={9.5} fill={hair} />
          <Rect x={44} y={22} width={12} height={8} fill={hair} />
        </G>
      );
    case 'ponytail':
      return (
        <G>
          <Path d="M25 46 q0 -29 25 -29 q25 0 25 29 l1 22 q-26 6 -52 0 z" fill={hair} />
          {/* Gathered behind the right ear and falling from there. */}
          <Ellipse cx={81} cy={58} rx={8} ry={18} fill={hair} />
          <Circle cx={76} cy={41} r={5} fill={hair} />
        </G>
      );
    case 'braid':
      return (
        <G>
          <Path d="M24 46 q0 -29 26 -29 q26 0 26 29 l1 20 q-27 6 -53 0 z" fill={hair} />
          {/* A plait over the left shoulder: three tapering knots. */}
          <Ellipse cx={24} cy={62} rx={7} ry={8} fill={hair} />
          <Ellipse cx={23} cy={74} rx={6} ry={7} fill={hair} />
          <Ellipse cx={22} cy={85} rx={5} ry={6} fill={hair} />
        </G>
      );
    case 'curly':
      return (
        <G>
          <Circle cx={30} cy={34} r={14} fill={hair} />
          <Circle cx={50} cy={24} r={16} fill={hair} />
          <Circle cx={70} cy={34} r={14} fill={hair} />
          <Circle cx={26} cy={50} r={12} fill={hair} />
          <Circle cx={74} cy={50} r={12} fill={hair} />
        </G>
      );
    default:
      return null;
  }
}

/** The part that covers the forehead. */
function HairFront({ style, hair }: { style: HairStyle; hair: string }) {
  switch (style) {
    case 'short':
      return <Path d={CAP_SHORT} fill={hair} />;
    case 'wavy':
      return <Path d={CAP_WAVY} fill={hair} />;
    case 'crop':
      return <Path d={CAP_CROP} fill={hair} />;
    case 'parted':
      return (
        <G>
          <Path d={CAP_SHORT} fill={hair} />
          {/* The part: a lighter groove combed off to one side, which is what
              separates this from plain short hair at 34px. */}
          <Path
            d="M41 21 q3 7 2.5 13 q-2 -6 -6 -9 z"
            fill="#FFFFFF"
            fillOpacity={0.16}
          />
        </G>
      );
    case 'curly':
      // Raised: at r=11 centred on y=32 the lower edge landed on the brows and
      // buried them.
      return (
        <G>
          <Circle cx={35} cy={28} r={10} fill={hair} />
          <Circle cx={50} cy={23} r={11} fill={hair} />
          <Circle cx={65} cy={28} r={10} fill={hair} />
        </G>
      );
    default:
      return <Path d={CAP_FULL} fill={hair} />;
  }
}

function Facial({ kind, hair }: { kind: Persona['facial']; hair: string }) {
  if (kind === 'beard') {
    // Follows the jaw and stops short of the mouth. The first version was a
    // solid blob across the whole lower face and read as a mask, not a beard.
    return (
      <G>
        <Path
          d="M30 48 q0 26 20 26 q20 0 20 -26 q-2 14 -6 18 q-5 5 -14 5 q-9 0 -14 -5 q-4 -4 -6 -18 z"
          fill={hair}
        />
        <Path d="M42 58.4 q8 -2.2 16 0 q-8 1.8 -16 0 z" fill={hair} />
      </G>
    );
  }
  if (kind === 'stubble') {
    return (
      <Path
        d="M31 57 q1 16 19 16 q18 0 19 -16 q-19 7 -38 0 z"
        fill={hair}
        fillOpacity={0.45}
      />
    );
  }
  if (kind === 'moustache') {
    return (
      <Path
        d="M40 58 q5 -1.7 10 -1.7 q5 0 10 1.7 q-5 0.9 -10 0.9 q-5 0 -10 -0.9 z"
        fill={hair}
      />
    );
  }
  return null;
}

/** Eyes, brows, nose and mouth are shared — only colour and hair differ. */
function Features({ hair }: { hair: string }) {
  return (
    <G>
      <Path d="M38 41 q5 -3 10 -0.5" stroke={hair} strokeWidth={2.2} strokeLinecap="round" fill="none" />
      <Path d="M62 41 q-5 -3 -10 -0.5" stroke={hair} strokeWidth={2.2} strokeLinecap="round" fill="none" />
      <Ellipse cx={42} cy={47} rx={2.6} ry={3.1} fill="#2A2028" />
      <Ellipse cx={58} cy={47} rx={2.6} ry={3.1} fill="#2A2028" />
      <Circle cx={42.9} cy={46} r={0.9} fill="#FFFFFF" fillOpacity={0.85} />
      <Circle cx={58.9} cy={46} r={0.9} fill="#FFFFFF" fillOpacity={0.85} />
      <Path d="M50 49 v5 q0 1.6 -2 2" stroke="#8A5B3C" strokeWidth={1.6} strokeLinecap="round" fill="none" />
      <Path d="M44 61 q6 4.5 12 0" stroke="#8A4E44" strokeWidth={2.2} strokeLinecap="round" fill="none" />
    </G>
  );
}

/** Horizontal and vertical scale about the centre of the head. */
const BUILDS = {
  oval: [1, 1],
  round: [1.07, 0.96],
  long: [0.94, 1.05],
} as const;

export function Portrait({ person, size = 84 }: { person: Persona; size?: number }) {
  const { skin, shade } = SKINS[person.skin];
  const hair = HAIRS[person.hair];
  const clothes = CLOTHES[person.clothes];
  const bg = BGS[person.bg];
  const clip = `portrait-${person.id}`;
  const [sx, sy] = BUILDS[person.build ?? 'oval'];

  return (
    <Svg width={size} height={size} viewBox="0 0 100 100">
      <Defs>
        <ClipPath id={clip}>
          <Circle cx={50} cy={50} r={50} />
        </ClipPath>
      </Defs>

      <G clipPath={`url(#${clip})`}>
        <Rect x={0} y={0} width={100} height={100} fill={bg} />

        {/* Drawn larger than the frame and nudged up: at 34px in the chat
            header a head that politely fits inside the circle stops reading as
            a face at all. 1.09 was too far — it clipped the tops of buns. */}
        <G transform="translate(-2.5, -3) scale(1.05)">
          <G transform={`translate(50 50) scale(${sx} ${sy}) translate(-50 -50)`}>
          <HairBack style={person.style} hair={hair} />

          {/* Shoulders first, then the neck, so the neck tucks behind a collar. */}
          <Ellipse cx={50} cy={112} rx={40} ry={34} fill={clothes} />
          <Rect x={42} y={62} width={16} height={20} rx={7} fill={shade} />

          <Ellipse cx={27} cy={48} rx={4} ry={5.5} fill={shade} />
          <Ellipse cx={73} cy={48} rx={4} ry={5.5} fill={shade} />
          <Ellipse cx={50} cy={46} rx={22} ry={26} fill={skin} />

          <Facial kind={person.facial} hair={hair} />
          <HairFront style={person.style} hair={hair} />
          <Features hair={hair} />
          </G>
        </G>
      </G>
    </Svg>
  );
}

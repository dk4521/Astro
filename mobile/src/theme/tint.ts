/**
 * What colour the screen you are on is.
 *
 * The home grid gave every destination a hue, and a hub only teaches a colour
 * if the screen behind the card wears it too — otherwise the grid is decoration
 * that ends the moment you tap it. Rather than thread a tint prop through two
 * dozen cards by hand, the shared `Card` and `Button` ask the router where they
 * are and colour themselves. A screen added later is tinted the day it gets a
 * row in `destinations.ts`, with nothing to remember.
 *
 * The screens outside that list are the ones you pass through rather than visit
 * — the way in, and the till — so they are coloured here instead.
 */

import { usePathname } from 'expo-router';

import { DESTINATIONS } from '../destinations';
import { colors, elementGlow } from './index';

/**
 * The routes that have no card on the home grid.
 *
 * **Onboarding** takes water, from the element palette — a hue the app already
 * owns and no destination has taken.
 *
 * **The account screens take green**, which is the colour their one button
 * already is. `signIn` is a meaning, not a decoration, so it wins over any tint
 * a screen might hand it; declaring the screen green makes the rest of the
 * screen agree with the button instead of arguing with it. Lightened from
 * `colors.signIn`, which is a fill colour and too dark to read as a border.
 */
const ELSEWHERE: { prefix: string; tint: string }[] = [
  { prefix: '/onboarding', tint: elementGlow.water },
  { prefix: '/sign-in', tint: '#3FA47B' },
  { prefix: '/sign-up', tint: '#3FA47B' },
];

export function useScreenTint(): string {
  const pathname = usePathname();
  // `/learn/nakshatras` belongs to Learn, the same way the sidebar row stays
  // lit on a chapter page.
  const here = DESTINATIONS.find(
    (destination) =>
      pathname === destination.route || pathname.startsWith(`${destination.route}/`),
  );
  if (here) return here.tint;

  const elsewhere = ELSEWHERE.find(
    (route) => pathname === route.prefix || pathname.startsWith(`${route.prefix}/`),
  );
  // The brand accent is the last resort, not a fifth entry above: a route that
  // reaches it is one nobody has thought about, and it should look ordinary
  // rather than wear a colour that claims to mean something.
  return elsewhere?.tint ?? colors.accent;
}

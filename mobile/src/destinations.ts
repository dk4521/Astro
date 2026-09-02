/**
 * Where the app can go, in one list.
 *
 * The sidebar and the home grid are two views of the same set, and they were
 * about to be two hand-kept copies of it — a screen added to one and forgotten
 * in the other is the ordinary way that goes wrong. Route, glyph and who may
 * see it live here; what each one is *called* lives in `i18n.ts` under the same
 * key, because the grid is translated and the sidebar is not.
 *
 * Home itself is deliberately absent. It is a row in the sidebar and nothing
 * else — a card on the home screen leading to the home screen is furniture.
 */

import type { HubKey } from './i18n';

export type Destination = {
  key: HubKey;
  route: string;
  /** The sidebar row's mark. The home card draws its own icon instead. */
  glyph: string;
  /**
   * The card's colour: its border, its icon and the wash behind it.
   *
   * One hue per destination and nowhere else in the app, so the grid is
   * navigable by colour after a week of use — the way a person finds an app on
   * a home screen without reading a single label. Taken from the palette in
   * `theme/index.ts` rather than invented, so they stay a family.
   */
  tint: string;
  /** Sits beside the title on the card, the way the reference sheet has it. */
  emoji: string;
  /** Hidden without an account, because the screen behind it would be empty. */
  accountOnly?: boolean;
  /**
   * Drawn in its own colour in the sidebar rather than the list's grey.
   *
   * One row has it, and one row should: everything else in the list is a place
   * you already own, and a price list that looks exactly like them is a price
   * list nobody opens. This is the whole extent of the selling — a colour, in
   * the same list, in the same order. No badge, no count, nothing that moves.
   */
  promote?: boolean;
};

export const DESTINATIONS: Destination[] = [
  { key: 'today', route: '/today', glyph: '☉', tint: '#F5A65B', emoji: '☀️' },
  { key: 'chart', route: '/chart', glyph: '◈', tint: '#79B4F5', emoji: '🔯' },
  { key: 'matching', route: '/matching', glyph: '◎', tint: '#F3719B', emoji: '💞' },
  // A crescent rather than a card suit: ♠ reads as poker, and the stock
  // Android font is missing enough of the prettier symbols that the power
  // glyph in the sidebar once shipped as an empty box.
  { key: 'tarot', route: '/tarot', glyph: '☾', tint: '#E8B84B', emoji: '🎴' },
  { key: 'chat', route: '/reading', glyph: '❋', tint: '#B98CFF', emoji: '💬' },
  // Only with an account: a signed-out phone keeps no conversations at all, so
  // the row would lead to a permanently empty screen.
  { key: 'history', route: '/history', glyph: '↺', tint: '#A9B2C6', emoji: '🕘', accountOnly: true },
  { key: 'learn', route: '/learn', glyph: '✦', tint: '#6FD2A8', emoji: '📖' },
  // Gold, which is what `send` already means everywhere in this app: this is
  // the row where something is spent.
  { key: 'plans', route: '/plans', glyph: '★', tint: '#E8B84B', emoji: '👑', promote: true },
  { key: 'settings', route: '/settings', glyph: '⚙', tint: '#8FAAE0', emoji: '⚙️' },
];

/** By key, for the home screen, which lays its cards out by hand. */
export const DESTINATION = Object.fromEntries(
  DESTINATIONS.map((destination) => [destination.key, destination]),
) as Record<HubKey, Destination>;

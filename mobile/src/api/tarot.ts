/**
 * The spread on the device.
 *
 * Two different reasons to keep things here, and they are worth telling apart.
 *
 * **The draw is kept because it is the reader's.** A spread is a moment, not a
 * computation: leaving the screen and coming back to three face-down cards
 * again would throw away something that cannot be recovered by asking the
 * server nicely. The seed makes that cheap — the whole spread is twelve hex
 * characters, and re-dealing it is a free, deterministic call.
 *
 * **The reading is kept because it cost something to make.** Not money any
 * more — Pro covers it — but a model call and several seconds of waiting, and
 * throwing that away when the screen unmounts is rude to the reader and
 * wasteful to us. Keyed by the seed *and* the question, so asking a different
 * question of the same three cards is a new reading, which is what it is.
 *
 * The deck is kept for the ordinary reason: it is 78 cards of static prose, it
 * should work on a train, and it should not be re-downloaded to open one card.
 */

import { TAROT_NAMESPACE, readCache, writeCache, clearNamespace } from './cache';
import { drawTarot, fetchTarotDeck, fetchTarotReading } from './client';
import type { DisplayLanguage } from '../i18n';
import type { TarotDeck, TarotDraw, TarotReading } from './types';

const DECK_KEY = `${TAROT_NAMESPACE}deck.v1`;
const DRAW_KEY = `${TAROT_NAMESPACE}draw.v1`;
const READING_KEY = (seed: string, language: string) =>
  `${TAROT_NAMESPACE}reading.${seed}.${language}.v1`;

/** A reading, stored with the question it answered. */
type StoredReading = { question: string; reading: TarotReading };

/**
 * The deck, network first.
 *
 * Same policy as the course index, for the same reason: card meanings are prose
 * and prose gets corrected, so being fresh whenever the phone is online matters
 * more than saving a small request. Serving a stale deck offline is right —
 * an old meaning beats an empty screen.
 */
export async function loadTarotDeck(): Promise<TarotDeck> {
  try {
    const deck = await fetchTarotDeck();
    await writeCache(DECK_KEY, deck);
    return deck;
  } catch (error) {
    const cached = await readCache<TarotDeck>(DECK_KEY);
    if (cached) return cached;
    throw error;
  }
}

/**
 * A spread as the reader left it — including which cards they had turned over.
 *
 * The reveal state is stored with the draw rather than reconstructed. Coming
 * back to three cards that are all face-up when only one had been turned would
 * quietly hand over the two the reader had not yet looked at, which is the one
 * thing the interaction is for.
 */
export type StoredDraw = { draw: TarotDraw; revealed: string[] };

export async function loadLastDraw(): Promise<StoredDraw | null> {
  const stored = await readCache<StoredDraw>(DRAW_KEY);
  // Guard against a shape from an older build: a half-read spread would render
  // as three blank cards rather than as nothing at all.
  const drawn = stored?.draw;
  if (!drawn?.seed || !Array.isArray(drawn.cards) || drawn.cards.length !== 3) {
    return null;
  }
  return { draw: drawn, revealed: Array.isArray(stored?.revealed) ? stored.revealed : [] };
}

/**
 * Shuffle, and drop the previous spread's readings.
 *
 * Pruned on the way in rather than on the way out: once a new hand is dealt the
 * old seed is unreachable from this screen, and its reading would otherwise sit
 * on the device forever. Nothing is lost that cannot be dealt again from its
 * seed.
 */
export async function newDraw(): Promise<TarotDraw> {
  const drawn = await drawTarot();
  await clearNamespace(`${TAROT_NAMESPACE}reading.`);
  await writeCache(DRAW_KEY, { draw: drawn, revealed: [] } satisfies StoredDraw);
  return drawn;
}

/** Remember which cards have been turned over. */
export async function rememberRevealed(draw: TarotDraw, revealed: string[]): Promise<void> {
  await writeCache(DRAW_KEY, { draw, revealed } satisfies StoredDraw);
}

/**
 * The reading for this spread.
 *
 * Returns the stored one when the same question is asked of the same cards in
 * the same language — including across a reinstall of the screen, an app
 * restart, or a phone that went offline in between. A different question is a
 * different reading and goes to the server.
 *
 * The cache is now a courtesy rather than an economy. It used to save the
 * reader a credit; a subscription has no credits, so what it saves is a wait
 * and a model call. Worth keeping for both.
 *
 * An ungrounded reading is never kept, exactly as on the chart side: the app's
 * one visible failure should not be served back all day.
 */
export async function loadTarotReading(
  seed: string,
  question: string,
  language: DisplayLanguage,
): Promise<TarotReading> {
  const key = READING_KEY(seed, language);

  const stored = await readCache<StoredReading>(key);
  if (stored && stored.question === question) return stored.reading;

  const reading = await fetchTarotReading({
    seed,
    question: question.trim() ? question : null,
    language,
  });

  if (reading.grounded) {
    await writeCache(key, { question, reading } satisfies StoredReading);
  }

  return reading;
}

/** Whatever was already read for this spread, without asking the server. */
export async function cachedTarotReading(
  seed: string,
  language: DisplayLanguage,
): Promise<StoredReading | null> {
  return readCache<StoredReading>(READING_KEY(seed, language));
}

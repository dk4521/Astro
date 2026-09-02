/**
 * Noticing when a question is not really about astrology.
 *
 * This used to live in `api/allowance.ts`, next to the credit balance, because
 * the only place it was needed was the screen someone met when they ran out of
 * messages. The balance is gone — the product sells a subscription now, not a
 * currency — and this is the part of that file worth keeping. It moved here
 * rather than into the paywall, because what it does has nothing to do with
 * money and everything to do with who is on the other end.
 *
 * **What it decides.** Only what a blocked person sees first. Someone who has
 * hit the paywall while saying this must not meet an upgrade prompt, so they
 * meet real numbers instead.
 *
 * **What it does not decide.** Whether help is offered at all. The blocked
 * panel carries the helplines quietly even when this returns false, because
 * keyword matching misses phrasings it has not been taught — and the cost of
 * missing one here is not a worse conversion rate.
 */

const CRISIS = new RegExp(
  [
    // English
    'kill myself', 'end my life', 'want to die', "don't want to live",
    'dont want to live', 'no point in living', 'suicide', 'hurt myself',
    'end it all', 'hits me', 'beats me', 'hitting me',
    // Hinglish
    'jeena nahi', 'jina nahi', 'mar jau', 'mar jaun', 'marna chahta',
    'marna chahti', 'khatam kar du', 'khatam kar doon', 'maarta hai',
    'maarti hai', 'peeta hai',
    // Devanagari
    'जीना नहीं', 'मर जाऊ', 'मरना चाहत', 'ख़त्म कर द', 'खत्म कर द',
    'आत्महत्या', 'मारता है', 'मारती है', 'पीटता है',
  ].join('|'),
  'i',
);

/** Whether a message looks like it comes from someone in trouble. */
export function looksLikeCrisis(text: string): boolean {
  return CRISIS.test(text);
}

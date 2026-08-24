/**
 * What the reader is allowed, now that it is a balance rather than a limit.
 *
 * **One currency.** A message costs one credit. Credits arrive from three
 * places that differ only in how long they last: six a day that expire at
 * midnight, a month's worth from a subscription that expire with the period,
 * and packs that were bought outright and last a year. The database spends
 * whichever expires soonest, so the free six are always used before anything
 * paid for — and this screen never has to explain which pocket a message came
 * out of.
 *
 * **The number is not kept on the device.** It comes from `credit_summary()`,
 * a Supabase function that reads the account's live lots. Reinstalling the app
 * or clearing its data changes nothing. Reading it also mints the day's free
 * credits if they are missing, which is why there is no scheduled job anywhere
 * in this product.
 *
 * **This is a display, not a gate.** That is the difference from the version
 * before it. `/v1/chat` now verifies the Supabase token and spends the credit
 * itself, so a modified client that ignores everything here gets a 402 from
 * the server rather than a free answer. Which is what lets the function below
 * fall open when Supabase cannot be reached: being wrong in the generous
 * direction costs nothing now, and being wrong in the other direction would
 * shut the door on someone mid-conversation for a reason that is not theirs.
 */

import { supabase } from '../auth/client';

/** Below this many left, the screen starts saying so. Above it, silence. */
export const QUIET_ABOVE = 3;

/** What the daily grant is worth. Mirrored in `ensure_free_grant()`. */
export const FREE_PER_DAY = 6;

export type Plan = 'free' | 'monthly' | 'yearly';

export type Allowance = {
  /** False when there is no account, so the caller can stay quiet about it. */
  signedIn: boolean;
  /** Live credits: everything not yet spent and not yet expired. */
  balance: number;
  /** When the soonest-expiring live credits die. Usually tonight. */
  expiresAt: Date | null;
  plan: Plan;
  /** Razorpay's word for the subscription's state, when there is one. */
  status: string | null;
  /** Paid up to here. What "cancelled" still entitles someone to. */
  periodEnd: Date | null;
};

const UNKNOWN: Allowance = {
  signedIn: false,
  balance: FREE_PER_DAY,
  expiresAt: null,
  plan: 'free',
  status: null,
  periodEnd: null,
};

function asDate(value: unknown): Date | null {
  if (typeof value !== 'string') return null;
  const parsed = new Date(value);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

function asPlan(value: unknown): Plan {
  return value === 'monthly' || value === 'yearly' ? value : 'free';
}

/**
 * The account's balance right now.
 *
 * One round trip, because the chat screen needs the number, what expires next
 * and whether a subscription is behind it — and three queries to draw one line
 * of text is three chances for them to disagree.
 */
export async function loadAllowance(userId: string | null): Promise<Allowance> {
  if (!supabase || !userId) return UNKNOWN;

  try {
    const { data, error } = await supabase.rpc('credit_summary');
    if (error || !data || typeof data !== 'object') return UNKNOWN;

    const row = data as Record<string, unknown>;
    return {
      signedIn: row.signed_in === true,
      balance: typeof row.balance === 'number' ? row.balance : 0,
      expiresAt: asDate(row.expires_at),
      plan: asPlan(row.plan),
      status: typeof row.status === 'string' ? row.status : null,
      periodEnd: asDate(row.period_end),
    };
  } catch {
    return UNKNOWN;
  }
}

/** Whether the plan behind this balance is a paid one that is still running. */
export function isSubscribed(allowance: Allowance | null): boolean {
  return Boolean(allowance && allowance.plan !== 'free' && allowance.status === 'active');
}

/**
 * Whether a message looks like it comes from someone in trouble.
 *
 * Used for one thing only: deciding what a person sees when they have run out.
 * Someone who has hit the wall while saying this must not meet an upgrade
 * prompt, so they meet real numbers instead.
 *
 * Keyword matching, with everything that implies. It will miss phrasings it has
 * not been taught — which is exactly why the exhausted screen carries the
 * helplines quietly even when this returns false. The check decides what
 * *leads*, never whether help is offered at all.
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

export function looksLikeCrisis(text: string): boolean {
  return CRISIS.test(text);
}

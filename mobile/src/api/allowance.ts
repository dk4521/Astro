/**
 * How many messages the reader has left today.
 *
 * **Where the numbers live and why.** The count is not kept on the device. It
 * comes from `messages_sent_today()`, a Supabase function that counts the rows
 * the account actually wrote — so reinstalling the app, clearing its data or
 * editing anything local changes nothing. The plan comes from `profiles.plan`,
 * which the row-level policy will not let a client write: an app that can raise
 * its own plan has not got a plan, it has got a suggestion.
 *
 * **What this is not.** It is still the app that decides whether to send. A
 * modified client could call `/v1/chat` directly and the backend would answer,
 * because the backend is stateless and has never been told who is asking. Real
 * enforcement means passing the Supabase token to FastAPI and having it verify
 * and count — worth doing before anything is charged for, and deliberately not
 * pretended to be done here.
 *
 * **Counted per day, not per conversation.** Per conversation was the first
 * plan and it does not survive contact: switching companion opens a new thread,
 * so fifteen companions would have meant fifteen allowances.
 */

import { supabase } from '../auth/client';

/** What each plan gets in a day. One place, so the UI and the gate agree. */
export const DAILY_LIMIT = { free: 6, paid: 50 } as const;

/** Below this many remaining, the screen starts saying so. Above it, silence. */
export const QUIET_ABOVE = 3;

export type Plan = keyof typeof DAILY_LIMIT;

export type Allowance = {
  plan: Plan;
  used: number;
  limit: number;
  remaining: number;
};

const UNKNOWN: Allowance = { plan: 'free', used: 0, limit: DAILY_LIMIT.free, remaining: DAILY_LIMIT.free };

/**
 * The account's allowance right now.
 *
 * Falls open rather than closed when Supabase cannot be reached. A network
 * blip must not tell someone they have run out — being wrong in the generous
 * direction costs a few model requests, and being wrong in the other direction
 * shuts the door on someone mid-conversation for a reason that is not theirs.
 */
export async function loadAllowance(userId: string | null): Promise<Allowance> {
  if (!supabase || !userId) return UNKNOWN;

  try {
    const [profile, count] = await Promise.all([
      supabase.from('profiles').select('plan').eq('id', userId).maybeSingle<{ plan: Plan }>(),
      supabase.rpc('messages_sent_today'),
    ]);

    const plan: Plan = profile.data?.plan === 'paid' ? 'paid' : 'free';
    const limit = DAILY_LIMIT[plan];
    const used = typeof count.data === 'number' ? count.data : 0;

    return { plan, used, limit, remaining: Math.max(0, limit - used) };
  } catch {
    return UNKNOWN;
  }
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

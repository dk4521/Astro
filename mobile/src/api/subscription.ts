/**
 * What the *server* believes about this subscription.
 *
 * The app already knows whether it is Pro — `usePurchases()` reads it from the
 * RevenueCat SDK, which is the right answer for deciding what a screen draws.
 * This asks the backend the same question, and exists for the case where the
 * two disagree.
 *
 * **Why that case matters.** The backend gates every AI endpoint on its own
 * answer, not on the app's, because a rooted phone can claim anything. So a
 * disagreement is not cosmetic: it is a person who has paid, whose app shows
 * them Pro, and whose questions come back 402. That happens for real reasons —
 * a purchase that never reached RevenueCat, a `logIn` that did not attach the
 * receipt to the account, a secret key that expired on the server — and without
 * this it is invisible from the inside and reads as theft from the outside.
 *
 * **Nothing gates on this.** It is a second opinion, not a source of truth for
 * the UI: it needs the network, and a paying subscriber on a train should not
 * lose their subscription because a request timed out. The SDK's cached answer
 * leads; this one is consulted when a purchase has just happened, and when a
 * request has just been refused.
 */

import { API_BASE_URL } from './client';
import { supabase } from '../auth/client';

export type BillingStatus = {
  /** False when the server has no RevenueCat key. Nothing is gated there. */
  enabled: boolean;
  signedIn: boolean;
  pro: boolean;
  /** Null for lifetime *and* for no subscription. Read `pro` first. */
  expiresAt: Date | null;
  product: string | null;
};

/** Long enough for a cold Render instance to wake up, short enough to give up on. */
const TIMEOUT_MS = 12_000;

async function authHeader(): Promise<Record<string, string>> {
  if (!supabase) return {};
  const { data } = await supabase.auth.getSession();
  const token = data.session?.access_token;
  return token ? { Authorization: `Bearer ${token}` } : {};
}

function parse(body: Record<string, unknown>): BillingStatus {
  const expires = typeof body.expires_at === 'string' ? new Date(body.expires_at) : null;
  return {
    enabled: body.enabled === true,
    signedIn: body.signed_in === true,
    pro: body.pro === true,
    expiresAt: expires && !Number.isNaN(expires.getTime()) ? expires : null,
    product: typeof body.product === 'string' ? body.product : null,
  };
}

async function ask(path: string, method: 'GET' | 'POST'): Promise<BillingStatus | null> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);

  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      method,
      headers: { Accept: 'application/json', ...(await authHeader()) },
      signal: controller.signal,
    });
    if (!response.ok) return null;
    return parse(await response.json());
  } catch {
    // Null means "could not ask", which every caller treats as "keep believing
    // the SDK". Distinguishing the reasons would not change what anyone does.
    return null;
  } finally {
    clearTimeout(timer);
  }
}

/** The server's answer, from its one-minute cache. */
export function fetchBillingStatus(): Promise<BillingStatus | null> {
  return ask('/v1/billing/status', 'GET');
}

/**
 * The server's answer with its cache dropped first.
 *
 * For the moment immediately after a purchase, and only then. Entitlements are
 * cached for a minute on the server, which is right for every read except the
 * one where a subscriber who has just been charged would otherwise be told,
 * accurately and uselessly, that a minute ago they had not paid.
 */
export function refreshBillingStatus(): Promise<BillingStatus | null> {
  return ask('/v1/billing/refresh', 'POST');
}

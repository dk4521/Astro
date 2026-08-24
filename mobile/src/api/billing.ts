/**
 * Buying credits.
 *
 * **Nothing native.** Razorpay's usual React Native integration is a native
 * module, which would mean this app can no longer be opened in Expo Go and
 * every contributor needs a development build before they can reach the chat
 * screen. Instead the backend creates a hosted Razorpay page and this module
 * opens its URL. UPI, cards and netbanking all work on that page, and it is
 * maintained by Razorpay rather than by us.
 *
 * **The app never names a price.** It sends a plan id. The amount, the credit
 * count and the account are all decided on the server, from a catalogue the
 * device cannot edit. A checkout call that accepted an amount would be a
 * checkout call that sells a year for one rupee.
 *
 * **Coming back is not how credits arrive.** The browser returning is a
 * convenience for the person watching; it can be lost to a closed tab or a
 * dead battery. Credits are granted by a signed webhook that Razorpay retries
 * until the server answers. So this module does not read a result out of the
 * redirect — it comes back and asks the balance, repeatedly, for a few
 * seconds.
 */

import * as WebBrowser from 'expo-web-browser';

import { ApiError, API_BASE_URL } from './client';
import { supabase } from '../auth/client';

export type BillingPlan = {
  id: string;
  kind: 'pack' | 'subscription';
  label: string;
  amount_paise: number;
  rupees: number;
  credits: number;
  period: 'monthly' | 'yearly' | null;
  validity_days: number | null;
};

export type Catalogue = {
  /** False when this deployment has no Razorpay keys. Hide the screen. */
  enabled: boolean;
  currency: string;
  plans: BillingPlan[];
};

/**
 * Where the payment page sends the browser back to.
 *
 * Left to the server to decide, and usually unset: Razorpay validates
 * `callback_url` and a custom scheme like `kosmiq://` is not always accepted.
 * Nothing depends on it — dismissing the browser returns control just as well,
 * and the balance is read afterwards either way.
 */
const RETURN_URL = 'kosmiq://billing';

/**
 * Long enough for Razorpay to create an order, short enough that a button does
 * not sit on "Opening…" forever. Creating a payment link is one API call on
 * their side, not a model request.
 */
const TIMEOUT_MS = 20_000;

async function timed(path: string, init: RequestInit): Promise<Response> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), TIMEOUT_MS);
  try {
    return await fetch(`${API_BASE_URL}${path}`, { ...init, signal: controller.signal });
  } catch (error) {
    const timedOut = error instanceof Error && error.name === 'AbortError';
    throw new ApiError(
      timedOut ? 'The server took too long. Try again.' : 'Could not reach the server.',
    );
  } finally {
    clearTimeout(timer);
  }
}

async function authed<T>(path: string, body?: unknown): Promise<T> {
  const { data } = (await supabase?.auth.getSession()) ?? { data: { session: null } };
  const token = data.session?.access_token;
  if (!token) throw new ApiError('Sign in to continue.', 401);

  const response = await timed(path, {
    method: body === undefined ? 'GET' : 'POST',
    headers: { 'Content-Type': 'application/json', Authorization: `Bearer ${token}` },
    body: body === undefined ? undefined : JSON.stringify(body),
  });

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const parsed = await response.json();
      if (typeof parsed?.detail === 'string') detail = parsed.detail;
    } catch {
      // Not JSON; the status-based message stands.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

/**
 * What is for sale, according to the server.
 *
 * Deliberately not bundled with the app. A store build from six months ago
 * still draws today's prices — and, more to the point, cannot draw a price
 * this server would refuse to charge.
 *
 * Unauthenticated, so the pricing screen can be looked at before signing in.
 */
export async function fetchPlans(): Promise<Catalogue> {
  const response = await timed('/v1/billing/plans', { method: 'GET' });
  if (!response.ok) throw new ApiError('Could not load plans.', response.status);
  return (await response.json()) as Catalogue;
}

export type CheckoutOutcome = 'paid' | 'dismissed' | 'pending';

/**
 * Open checkout for one plan and wait for the person to finish with it.
 *
 * Resolves `paid` only once the balance has actually moved — not when the
 * browser closed, which says nothing. `pending` means the browser came back
 * and the webhook had not landed yet; a payment that succeeded will still show
 * up, so the screen says "this can take a moment" rather than "it failed".
 */
export async function checkout(
  planId: string,
  balanceNow: () => Promise<number>,
): Promise<CheckoutOutcome> {
  const before = await balanceNow();

  const { url } = await authed<{ url: string; reference: string; kind: string }>(
    '/v1/billing/checkout',
    { plan_id: planId },
  );

  // `openAuthSessionAsync` rather than `openBrowserAsync` for one reason: it
  // resolves when the browser is dismissed *or* when the return URL fires, so
  // the flow does not stall on a redirect Razorpay may never have accepted.
  const result = await WebBrowser.openAuthSessionAsync(url, RETURN_URL);
  if (result.type === 'cancel' || result.type === 'dismiss') {
    // Not a failure. Someone may have paid and then closed the tab manually,
    // so the balance is still worth checking before saying anything.
    const settled = await waitForCredits(before, balanceNow, 3);
    return settled ? 'paid' : 'dismissed';
  }

  return (await waitForCredits(before, balanceNow)) ? 'paid' : 'pending';
}

/**
 * Poll until the balance rises, or give up quietly.
 *
 * Polling rather than a subscription because the thing being waited on is a
 * webhook arriving at another machine, and the number of times this runs in a
 * person's life is roughly the number of times they buy something.
 */
export async function waitForCredits(
  before: number,
  balanceNow: () => Promise<number>,
  attempts = 8,
  everyMs = 2000,
): Promise<boolean> {
  for (let i = 0; i < attempts; i += 1) {
    await new Promise((resolve) => setTimeout(resolve, everyMs));
    try {
      if ((await balanceNow()) > before) return true;
    } catch {
      // A failed poll is not a failed payment; keep trying.
    }
  }
  return false;
}

/** Stop a subscription at the end of the period already paid for. */
export async function cancelSubscription(): Promise<string> {
  const result = await authed<{ status: string; detail: string }>('/v1/billing/cancel', {});
  return result.detail;
}

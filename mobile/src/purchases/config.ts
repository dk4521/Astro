/**
 * Which RevenueCat project this build talks to, and what it sells.
 *
 * **The key is per platform, and one of them is not shippable.** RevenueCat
 * issues a separate publishable key for the App Store and for Google Play, plus
 * a `test_` key for the Test Store — a sandbox that answers with fake products
 * so a paywall can be built before a single product exists in App Store Connect.
 * That key is the one to develop against and the one that must never reach a
 * store build: an app shipped with it sells nothing and reports every customer
 * as entitled. `REVENUECAT_NOT_CONFIGURED` below is that check, written in the
 * same shape as `API_NOT_CONFIGURED` in `../api/client` and for the same
 * reason — a deployment mistake should name itself on the settings screen
 * rather than being discovered from a support email.
 *
 * **These keys are publishable.** They identify the project to RevenueCat and
 * are designed to sit inside a shipped binary, which is why they live in
 * `EXPO_PUBLIC_*` alongside the Supabase anon key rather than in a secret
 * store. The secret half of RevenueCat is the v2 API key, which belongs to the
 * backend and appears nowhere in this app.
 *
 * **Entitlement, not product.** Every gate in this app asks one question —
 * is `kosmiq_pro` active — and never which SKU paid for it. That is the whole
 * point of an entitlement: the three products below can be renamed, re-priced,
 * regionalised or replaced from the dashboard without a release, because no
 * screen names them.
 */

import { Platform } from 'react-native';

/**
 * The one entitlement this app gates on.
 *
 * Configured in the RevenueCat dashboard and attached to all three products, so
 * a monthly subscriber, a yearly subscriber and someone who bought lifetime all
 * arrive here identically.
 */
export const PRO_ENTITLEMENT = 'kosmiq_pro';

/**
 * The offering the paywall loads by default.
 *
 * Left as `null` deliberately: passing no offering makes the SDK use whichever
 * one is marked *current* in the dashboard, which is what lets a price test or
 * a festival offer be switched on without shipping anything. Name an offering
 * here only to pin this build to one on purpose.
 */
export const DEFAULT_OFFERING: string | null = null;

/**
 * The products, as configured in the stores and mapped in RevenueCat.
 *
 * Nothing in the app reads a price from this table — prices come from the store,
 * already localised and already in the reader's currency, and hard-coding one
 * is how an app ends up showing ₹499 to someone who will be charged $9.99.
 * These identifiers exist for two honest uses: matching a package back to a
 * label when drawing a custom list, and being greppable when someone asks what
 * this app sells.
 *
 * **Weekly is here because the market is India.** A week is what a lot of
 * people can commit to at a UPI price point, and a subscription nobody can
 * afford to start is not cheaper than one they can. It is also the term most
 * likely to be cancelled after one cycle, which is fine: a week of Pro that
 * ends is a better outcome than a month that was never bought.
 *
 * Adding one here changes nothing on its own. The offering in the RevenueCat
 * dashboard decides what the paywall shows, and the entitlement decides what
 * the app unlocks — which is why every gate asks about `kosmiq_pro` and no
 * screen names a product.
 */
export const PRODUCTS = {
  lifetime: 'lifetime',
  yearly: 'yearly',
  monthly: 'monthly',
  weekly: 'weekly',
} as const;

export type ProductKey = keyof typeof PRODUCTS;

/**
 * The key for the store this build will actually be bought from.
 *
 * Android and iOS keys are separate projects' worth of configuration on
 * RevenueCat's side; handing the iOS key to Google Play does not fail loudly,
 * it just returns an empty offering, which reads on screen as "nothing for
 * sale" rather than as a misconfiguration.
 */
function storeKey(): string | undefined {
  const key = Platform.select({
    ios: process.env.EXPO_PUBLIC_REVENUECAT_IOS_KEY,
    android: process.env.EXPO_PUBLIC_REVENUECAT_ANDROID_KEY,
    default: undefined,
  });
  return key?.trim() || undefined;
}

function testKey(): string | undefined {
  return process.env.EXPO_PUBLIC_REVENUECAT_TEST_KEY?.trim() || undefined;
}

/**
 * What to configure the SDK with, or `null` to leave it unconfigured.
 *
 * In development the Test Store key is a legitimate first choice: it lets the
 * paywall, the entitlement and the whole purchase flow be exercised on a device
 * before anyone has filled in a tax form. A real store key still wins when one
 * is present, because sandbox testing against the actual store is the only way
 * to catch a product that was mapped wrong.
 *
 * In release there is exactly one acceptable answer — the platform's own key.
 * A missing key and a `test_` key are both refused here rather than passed to
 * `configure`, because both produce an app that appears to work.
 */
function resolveApiKey(): string | null {
  const store = storeKey();

  if (__DEV__) return store ?? testKey() ?? null;

  // A Test Store key in a release build is the failure this function exists for.
  if (!store || store.startsWith('test_')) return null;
  return store;
}

export const REVENUECAT_API_KEY = resolveApiKey();

/**
 * True when a build has no usable key, so purchases are switched off.
 *
 * Not a thrown error. The rest of the app works without purchases: every chart,
 * dasha, panchang, match and card draw is arithmetic and needs no subscription
 * at all. A missing key hides the upgrade path and says so on the plans screen,
 * rather than leaving a button that opens an empty paywall.
 */
export const REVENUECAT_NOT_CONFIGURED = REVENUECAT_API_KEY === null;

/**
 * True when this build is pointed at the sandbox rather than a real store.
 *
 * Worth surfacing in development UI: a purchase made here costs nothing and
 * grants `kosmiq_pro` anyway, and someone testing needs to know that the
 * entitlement they are looking at is not evidence that billing works.
 */
export const USING_TEST_STORE = REVENUECAT_API_KEY?.startsWith('test_') ?? false;

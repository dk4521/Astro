/**
 * The RevenueCat SDK, wrapped so the screens never touch it directly.
 *
 * **Native, and that is a change.** Everything bought in this app until now went
 * through a hosted Razorpay page precisely so no native module was needed and
 * the app stayed openable in Expo Go. That path is deleted: Razorpay sold
 * credits, credits are gone, and selling digital goods inside an app through
 * anything but the store is against both platforms' rules anyway. `react-native-purchases` is native, and
 * it has to be: Apple and Google both require that digital goods consumed
 * inside an app are sold through their own billing, which is a StoreKit and a
 * Play Billing call, not a web page. Version 10 softens the cost — in Expo Go
 * the SDK detects the missing native module and swaps in JavaScript mocks, so
 * the app still *opens* and paywalls still *draw* there. Nothing charges. A
 * development build (`expo-dev-client`) is required before a purchase is real,
 * and `IS_PREVIEW` below exists so the UI can say which of the two it is
 * standing in rather than silently reporting a fake entitlement as a fact.
 *
 * **Configure exactly once, and never twice.** `Purchases.configure` is not
 * idempotent in a useful way — calling it again resets the SDK's identity and
 * throws away a customer info cache the app is mid-render on. React 19 in
 * development mounts effects twice on purpose, so a guard is not defensive
 * programming here, it is the difference between working and not.
 *
 * **Entitlements are the truth, not receipts.** Every question this module
 * answers is asked of `customerInfo.entitlements.active`, which RevenueCat
 * computes server-side from the store's own transaction record. That is what
 * makes lifetime, yearly and monthly indistinguishable to a caller, and what
 * makes an expired subscription disappear on its own without the app tracking
 * a single date.
 *
 * **The device is not the auditor.** What the SDK reports is good enough to
 * decide what a screen draws. It is not good enough to decide what the server
 * gives away: a rooted phone can say anything.
 *
 * That is no longer advice — it is how the backend works. Every endpoint that
 * calls a model reads the entitlement from RevenueCat's own API with a secret
 * key (`backend/app/entitlements.py`) and answers 402 when it is not there,
 * whatever this SDK told the screen. `../api/subscription` asks the server for
 * that answer, so the two can be compared when they disagree.
 */

import { Platform } from 'react-native';
import Purchases, {
  LOG_LEVEL,
  PURCHASES_ERROR_CODE,
  type CustomerInfo,
  type PurchasesOffering,
  type PurchasesOfferings,
  type PurchasesPackage,
} from 'react-native-purchases';

import {
  DEFAULT_OFFERING,
  PRO_ENTITLEMENT,
  REVENUECAT_API_KEY,
  REVENUECAT_NOT_CONFIGURED,
} from './config';

/**
 * True when the SDK is running on its JavaScript mocks rather than a store.
 *
 * Two ways to get there: Expo Go, which the SDK flags on the `expo` global, and
 * web, where there is no native billing at all. The Expo Go half mirrors the
 * check the SDK itself uses to decide to mock, rather than sniffing for a
 * development build, so it stays correct if that detection moves.
 *
 * This says *nothing charges*, which is not the same as `USING_TEST_STORE` —
 * that one is a real RevenueCat backend serving fake products. Both need saying
 * out loud in the UI, for the same reason: an entitlement granted under either
 * is not evidence that billing works.
 */
export const IS_PREVIEW: boolean =
  Platform.OS === 'web' ||
  Boolean((globalThis as { expo?: { modules?: { ExpoGo?: boolean } } }).expo?.modules?.ExpoGo);

let configured = false;

/**
 * Start the SDK. Safe to call as often as the tree remounts.
 *
 * Returns whether the SDK is usable at all, so a caller can hide the upgrade
 * path rather than render a button that opens an empty paywall.
 */
export function configurePurchases(): boolean {
  if (configured) return true;
  if (REVENUECAT_NOT_CONFIGURED || !REVENUECAT_API_KEY) return false;

  // Before `configure`, or the first requests are logged at the old level.
  // Verbose in development is the documented first step for every "why is my
  // offering empty" question, and INFO in release keeps the store's own
  // diagnostics without narrating every cache hit into the device log.
  Purchases.setLogLevel(__DEV__ ? LOG_LEVEL.VERBOSE : LOG_LEVEL.INFO).catch(() => {
    // Log level is a convenience. Failing to set it is not worth refusing to
    // configure over.
  });

  // `appUserID: null` asks RevenueCat for an anonymous id. The account is
  // attached later by `identify()` if and when someone signs in — configuring
  // with a Supabase id we may not have yet would mean either delaying the SDK
  // until auth resolves, or configuring twice. Anonymous-then-alias is the
  // documented path and it keeps a purchase made before signing in attachable
  // to the account afterwards.
  Purchases.configure({
    apiKey: REVENUECAT_API_KEY,
    appUserID: null,
  });

  configured = true;
  return true;
}

export function isConfigured(): boolean {
  return configured;
}

/**
 * Attach purchases to a Supabase account, or let go of one.
 *
 * Called whenever the auth session changes. `logIn` aliases whatever the
 * anonymous user had bought onto the real id, which is what makes "bought it,
 * then made an account" not lose the purchase. `logOut` returns the SDK to a
 * fresh anonymous id so the next person to use the phone does not inherit
 * someone else's entitlement.
 *
 * Both are quiet on failure. A network blip while switching identity must not
 * take down the screen that triggered it — the SDK retries, and the next
 * `getCustomerInfo` corrects the picture.
 */
export async function identify(userId: string | null): Promise<CustomerInfo | null> {
  if (!configured) return null;

  try {
    if (userId) {
      const { customerInfo } = await Purchases.logIn(userId);
      return customerInfo;
    }

    // Logging out an already-anonymous user is an error, not a no-op, and it is
    // the normal state on a phone that has never signed in.
    if (await Purchases.isAnonymous()) return null;
    return await Purchases.logOut();
  } catch {
    return null;
  }
}

/** Whether `kosmiq_pro` is active on this customer. The only gate in the app. */
export function isPro(info: CustomerInfo | null): boolean {
  return Boolean(info?.entitlements.active[PRO_ENTITLEMENT]);
}

/**
 * When pro access runs out, or `null` for lifetime and for no access at all.
 *
 * RevenueCat reports lifetime as an active entitlement with no expiry, which is
 * the same shape as "not subscribed" if a caller only checks for a date. Every
 * reader of this must check `isPro` first.
 */
export function proExpiry(info: CustomerInfo | null): Date | null {
  const entitlement = info?.entitlements.active[PRO_ENTITLEMENT];
  if (!entitlement?.expirationDate) return null;
  const parsed = new Date(entitlement.expirationDate);
  return Number.isNaN(parsed.getTime()) ? null : parsed;
}

/**
 * Whether the subscription behind pro access will renew.
 *
 * False for lifetime too, which is correct but easy to misread: a lifetime
 * buyer is not renewing because there is nothing left to pay. Pair it with
 * `proExpiry() === null` before telling anyone their access is ending.
 */
export function willRenew(info: CustomerInfo | null): boolean {
  return Boolean(info?.entitlements.active[PRO_ENTITLEMENT]?.willRenew);
}

/** The customer as RevenueCat currently understands them. */
export async function getCustomerInfo(): Promise<CustomerInfo | null> {
  if (!configured) return null;
  try {
    return await Purchases.getCustomerInfo();
  } catch {
    // Cached info is served by the SDK when it can, so a failure here means
    // both the network and the cache were unavailable. Null, and the caller
    // keeps whatever it last knew.
    return null;
  }
}

/**
 * What is for sale, from the store.
 *
 * The prices inside are the store's own strings — already localised, already in
 * the buyer's currency, already carrying the introductory offer they personally
 * qualify for. `priceString` is always what to draw; the numeric `price` is for
 * arithmetic and never for display.
 */
export async function getOfferings(): Promise<PurchasesOfferings | null> {
  if (!configured) return null;
  try {
    return await Purchases.getOfferings();
  } catch {
    return null;
  }
}

/**
 * The offering a paywall should use: the pinned one if this build names one,
 * otherwise whichever the dashboard currently calls current.
 */
export async function getCurrentOffering(): Promise<PurchasesOffering | null> {
  const offerings = await getOfferings();
  if (!offerings) return null;
  if (DEFAULT_OFFERING) return offerings.all[DEFAULT_OFFERING] ?? offerings.current;
  return offerings.current;
}

export type PurchaseOutcome =
  | { status: 'purchased'; customerInfo: CustomerInfo }
  /** The buyer backed out. Not an error and never worth an alert. */
  | { status: 'cancelled' }
  /** Google Play's slow payment methods. The entitlement arrives later. */
  | { status: 'pending' }
  | { status: 'error'; message: string };

/**
 * Buy one package.
 *
 * Only needed for a hand-drawn price list — `presentPaywall` in `./paywall`
 * does its own purchasing and is the better default. This exists because the
 * plans screen already draws its own cards and a paywall that cannot be styled
 * to match a night sky is worse than one that can.
 *
 * Cancellation is separated from failure deliberately. It is by far the most
 * common way a purchase ends, it is a decision rather than a fault, and an app
 * that shows "Purchase failed" when someone pressed the X has told them
 * something untrue about their own action.
 */
export async function purchasePackage(pkg: PurchasesPackage): Promise<PurchaseOutcome> {
  if (!configured) return { status: 'error', message: 'Purchases are not available in this build.' };

  try {
    const { customerInfo } = await Purchases.purchasePackage(pkg);
    return { status: 'purchased', customerInfo };
  } catch (error) {
    return fromPurchaseError(error);
  }
}

/**
 * Restore purchases onto this device.
 *
 * Apple requires a visible way to do this in any app that sells a
 * non-consumable or a subscription, and review rejects builds without one. It
 * also genuinely matters: a lifetime buyer on a new phone has no other route
 * back to what they paid for.
 */
export async function restorePurchases(): Promise<
  { status: 'restored'; customerInfo: CustomerInfo } | { status: 'error'; message: string }
> {
  if (!configured) return { status: 'error', message: 'Purchases are not available in this build.' };

  try {
    return { status: 'restored', customerInfo: await Purchases.restorePurchases() };
  } catch (error) {
    const outcome = fromPurchaseError(error);
    return {
      status: 'error',
      message: outcome.status === 'error' ? outcome.message : 'Could not restore purchases.',
    };
  }
}

/**
 * Turn whatever the SDK threw into something a person can act on.
 *
 * The SDK throws an `Error` with RevenueCat's fields hung off it rather than a
 * typed class, so this reads defensively and falls back to the SDK's own
 * message. The codes handled by name are the ones with a *different action*
 * behind them: try again later, check your payment method, you already own
 * this. Everything else collapses to one honest sentence, because a numbered
 * error code shown to a reader is a code they will read out to nobody.
 */
function fromPurchaseError(error: unknown): PurchaseOutcome {
  const raw = error as { code?: string; message?: string; userCancelled?: boolean } | null;

  if (raw?.userCancelled || raw?.code === PURCHASES_ERROR_CODE.PURCHASE_CANCELLED_ERROR) {
    return { status: 'cancelled' };
  }

  switch (raw?.code) {
    // Google Play's pending purchases: bank transfer, cash at a counter. The
    // entitlement is granted when it clears, which may be days. Saying "failed"
    // here would be wrong in the most expensive direction.
    case PURCHASES_ERROR_CODE.PAYMENT_PENDING_ERROR:
      return { status: 'pending' };

    case PURCHASES_ERROR_CODE.PRODUCT_ALREADY_PURCHASED_ERROR:
      return {
        status: 'error',
        message: 'You already own this. Try Restore purchases.',
      };

    case PURCHASES_ERROR_CODE.NETWORK_ERROR:
    case PURCHASES_ERROR_CODE.OFFLINE_CONNECTION_ERROR:
      return { status: 'error', message: 'No connection. Try again when you are back online.' };

    case PURCHASES_ERROR_CODE.STORE_PROBLEM_ERROR:
      return { status: 'error', message: 'The store is having trouble. Try again in a moment.' };

    case PURCHASES_ERROR_CODE.PURCHASE_NOT_ALLOWED_ERROR:
      return {
        status: 'error',
        message: 'This device is not allowed to make purchases. Check your device restrictions.',
      };

    case PURCHASES_ERROR_CODE.PRODUCT_NOT_AVAILABLE_FOR_PURCHASE_ERROR:
      return { status: 'error', message: 'That plan is not available on this account yet.' };

    default:
      return {
        status: 'error',
        message: raw?.message || 'Could not complete the purchase.',
      };
  }
}

export type { CustomerInfo, PurchasesOffering, PurchasesPackage };

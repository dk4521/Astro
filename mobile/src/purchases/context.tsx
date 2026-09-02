/**
 * Pro access, for the whole app.
 *
 * One provider, mounted once, holding one boolean that matters: is
 * `enuma_sky_pro` active. Screens ask this provider rather than the SDK so that a
 * gate is a hook call rather than an async round trip — a component that has to
 * `await getCustomerInfo()` before it knows what to draw renders the locked
 * state first and then flips, which reads as the app taking something away.
 *
 * **`ready` is the whole reason this is a provider.** Mirrors `AuthProvider`
 * next door, and for the same failure: routing or gating on an entitlement that
 * has not loaded shows a paywall to a paying customer for a frame. That is the
 * single worst frame this app can render, so nothing gates until `ready`.
 *
 * **The listener is the point, not the fetch.** `addCustomerInfoUpdateListener`
 * fires on renewal, on expiry, on a restore, on a purchase made inside a
 * RevenueCat paywall this code never sees the result of, and on a Customer
 * Center cancellation. Without it, every one of those would need the screen
 * that caused it to remember to refresh — and the ones that happen while the
 * app is backgrounded would need something else entirely.
 *
 * **Identity follows Supabase.** `AuthProvider` is above this in the tree, so
 * the session is already resolved and this only has to mirror it. Purchases
 * made while signed out are aliased onto the account on sign-in, which is what
 * keeps "bought, then signed up" from losing the purchase.
 */

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useRef,
  useState,
  type ReactNode,
} from 'react';
import Purchases, { type CustomerInfo } from 'react-native-purchases';

import { useAuth } from '../auth/context';
import {
  configurePurchases,
  getCustomerInfo,
  identify,
  isPro,
  proExpiry,
  willRenew,
  IS_PREVIEW,
} from './client';
import { REVENUECAT_NOT_CONFIGURED, USING_TEST_STORE } from './config';

type PurchasesState = {
  /** False when this build has no usable RevenueCat key. Hide the upgrade path. */
  available: boolean;
  /** True once the first customer info has been resolved, whatever the answer. */
  ready: boolean;
  /** `enuma_sky_pro` is active. The only question most callers should ask. */
  pro: boolean;
  /** When access ends. Null for lifetime — check `pro` before reading this. */
  expiresAt: Date | null;
  /** False for lifetime *and* for a cancelled subscription still inside its term. */
  renews: boolean;
  customerInfo: CustomerInfo | null;
  /** Running on JS mocks (Expo Go / web): paywalls draw, nothing charges. */
  preview: boolean;
  /** Pointed at the Test Store sandbox rather than a real store. */
  sandbox: boolean;
  /** Re-read from the store. The listener covers the normal cases; this is for pull-to-refresh. */
  refresh: () => Promise<void>;
};

const PurchasesContext = createContext<PurchasesState | null>(null);

export function PurchasesProvider({ children }: { children: ReactNode }) {
  const { user, ready: authReady } = useAuth();

  const [customerInfo, setCustomerInfo] = useState<CustomerInfo | null>(null);
  // An unconfigured build has nothing to wait for, so it is ready immediately —
  // otherwise every gate in the app would hang on a fetch that will never run.
  const [ready, setReady] = useState(REVENUECAT_NOT_CONFIGURED);
  const [available] = useState(() => configurePurchases());

  // The listener must outlive re-renders but must not re-subscribe on each one:
  // the SDK keys removal on identity, so a new closure every render would leak
  // one subscription per render and fan every update out to all of them.
  const mounted = useRef(true);

  useEffect(() => {
    mounted.current = true;
    return () => {
      mounted.current = false;
    };
  }, []);

  useEffect(() => {
    if (!available) return;

    const listener = (info: CustomerInfo) => {
      if (mounted.current) setCustomerInfo(info);
    };

    Purchases.addCustomerInfoUpdateListener(listener);
    return () => {
      Purchases.removeCustomerInfoUpdateListener(listener);
    };
  }, [available]);

  // Identity, then a read. Ordered rather than parallel on purpose: `logIn`
  // returns the info for the account being switched *to*, and a `getCustomerInfo`
  // racing it can resolve with the outgoing user's entitlements and win.
  useEffect(() => {
    if (!available || !authReady) return;

    let cancelled = false;

    (async () => {
      const afterIdentity = await identify(user?.id ?? null);
      const info = afterIdentity ?? (await getCustomerInfo());

      if (cancelled || !mounted.current) return;
      setCustomerInfo(info);
      setReady(true);
    })();

    return () => {
      cancelled = true;
    };
  }, [available, authReady, user?.id]);

  const refresh = useCallback(async () => {
    if (!available) return;
    const info = await getCustomerInfo();
    // Null means both the network and the SDK's cache failed. Keeping the last
    // known answer is better than revoking access over a dropped connection.
    if (info && mounted.current) setCustomerInfo(info);
  }, [available]);

  const value = useMemo<PurchasesState>(
    () => ({
      available,
      ready,
      pro: isPro(customerInfo),
      expiresAt: proExpiry(customerInfo),
      renews: willRenew(customerInfo),
      customerInfo,
      preview: IS_PREVIEW,
      sandbox: USING_TEST_STORE,
      refresh,
    }),
    [available, ready, customerInfo, refresh],
  );

  return <PurchasesContext.Provider value={value}>{children}</PurchasesContext.Provider>;
}

export function usePurchases(): PurchasesState {
  const value = useContext(PurchasesContext);
  if (!value) throw new Error('usePurchases must be used inside PurchasesProvider');
  return value;
}

/**
 * Just the gate, for the many screens that only need the boolean.
 *
 * Unresolved counts as *not* pro. That is the safe direction for anything that
 * unlocks content — access is granted only once it has actually been seen — but
 * it collapses three states into two, and the state it hides is the one where a
 * paying customer briefly reads as unpaid.
 *
 * So this is the right hook for *adding* something (a "pro" badge, an extra
 * section) and the wrong one for *taking something away*. Anything that draws a
 * lock, a paywall or an upsell should use `usePurchases` and wait on `ready`,
 * or it will flash that lock at someone who has already paid.
 */
export function useIsPro(): boolean {
  const { ready, pro } = usePurchases();
  return ready && pro;
}

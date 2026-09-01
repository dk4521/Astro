/**
 * RevenueCat's own paywall and Customer Center, presented modally.
 *
 * **Why not draw it ourselves.** The plans screen already draws a price list in
 * this app's own colours, and it will keep doing so. What it cannot do is
 * change without a release. A dashboard paywall is edited by whoever is running
 * the product, ships to phones already installed, and can be A/B tested against
 * the current one — which is the whole reason to take the visual compromise of a
 * template that is not quite this app's night sky.
 *
 * **`presentPaywallIfNeeded` is the one to reach for.** It asks the entitlement
 * question and presents nothing if the answer is yes, which removes the one
 * genuinely embarrassing bug in this area: showing an upgrade screen to someone
 * who upgraded last week on another device.
 *
 * **The result is not the source of truth.** `PURCHASED` is a good signal to
 * refresh on, but the entitlement itself arrives through the customer info
 * listener in `./context`, which also catches the purchase the reader made in a
 * paywall this app opened and then forgot about. Treat what comes back here as
 * "something happened, look again", never as the grant itself.
 *
 * **Customer Center is not a nice-to-have on iOS.** Apple expects a subscriber
 * to be able to reach cancellation, and RevenueCat's Customer Center covers
 * cancel, change plan, restore, refund requests (iOS only) and the "where did
 * my purchase go" path in one sheet that is configured from the dashboard. It
 * replaces a settings screen this app would otherwise have to write, and get
 * wrong, twice — once per platform.
 */

import RevenueCatUI, { PAYWALL_RESULT } from 'react-native-purchases-ui';

import { getCurrentOffering, isConfigured } from './client';
import { PRO_ENTITLEMENT } from './config';

export { PAYWALL_RESULT };

/** What the caller actually needs to know after a paywall closed. */
export type PaywallOutcome =
  /** Bought or restored. The entitlement is live; refresh and move on. */
  | { status: 'entitled'; restored: boolean }
  /** Closed without buying, or never shown because they were already entitled. */
  | { status: 'dismissed'; alreadyEntitled: boolean }
  | { status: 'error'; message: string };

function interpret(result: PAYWALL_RESULT): PaywallOutcome {
  switch (result) {
    case PAYWALL_RESULT.PURCHASED:
      return { status: 'entitled', restored: false };
    case PAYWALL_RESULT.RESTORED:
      return { status: 'entitled', restored: true };
    // Only `presentPaywallIfNeeded` returns this, and only because the reader
    // already has what the paywall was going to sell them.
    case PAYWALL_RESULT.NOT_PRESENTED:
      return { status: 'dismissed', alreadyEntitled: true };
    case PAYWALL_RESULT.CANCELLED:
      return { status: 'dismissed', alreadyEntitled: false };
    case PAYWALL_RESULT.ERROR:
    default:
      return { status: 'error', message: 'The upgrade screen could not be opened.' };
  }
}

/**
 * Show the paywall for the current offering, whatever the reader already owns.
 *
 * For the "see the plans" button, where being shown the price list is the thing
 * that was asked for. Use `presentPaywallIfNeeded` for a gate.
 */
export async function presentPaywall(): Promise<PaywallOutcome> {
  if (!isConfigured()) {
    return { status: 'error', message: 'Purchases are not available in this build.' };
  }

  try {
    // Passing the offering explicitly rather than letting the SDK fetch it
    // again: `./context` and the plans screen have usually already warmed this
    // cache, and an offering that failed to load is worth reporting as such
    // instead of opening a paywall with no packages on it.
    const offering = await getCurrentOffering();
    if (!offering) {
      return { status: 'error', message: 'No plans are available right now.' };
    }

    return interpret(await RevenueCatUI.presentPaywall({ offering }));
  } catch (error) {
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'The upgrade screen could not be opened.',
    };
  }
}

/**
 * Show the paywall only if `kosmiq_pro` is not already active.
 *
 * The gate. The entitlement check happens inside the SDK against freshly
 * fetched customer info, so this is also the safest thing to call from a screen
 * that has not waited for the provider's `ready`.
 */
export async function presentPaywallIfNeeded(): Promise<PaywallOutcome> {
  if (!isConfigured()) {
    return { status: 'error', message: 'Purchases are not available in this build.' };
  }

  try {
    return interpret(
      await RevenueCatUI.presentPaywallIfNeeded({
        requiredEntitlementIdentifier: PRO_ENTITLEMENT,
      }),
    );
  } catch (error) {
    return {
      status: 'error',
      message: error instanceof Error ? error.message : 'The upgrade screen could not be opened.',
    };
  }
}

/**
 * Open the Customer Center: manage, cancel, change plan, restore, refund.
 *
 * `onDone` fires after the sheet closes having plausibly changed something, so
 * the caller can re-read entitlements. It is deliberately coarse — the listener
 * in `./context` is what actually keeps state correct, and this is only here to
 * spare a screen from waiting on it.
 */
export async function presentCustomerCenter(onDone?: () => void): Promise<void> {
  if (!isConfigured()) return;

  try {
    await RevenueCatUI.presentCustomerCenter({
      callbacks: {
        onRestoreCompleted: () => onDone?.(),
        // Cancelling leaves through the store's own sheet, so the entitlement
        // does not change while the Customer Center is open — but `willRenew`
        // does, and that is what the plans screen prints.
        onShowingManageSubscriptions: () => onDone?.(),
        onManagementOptionSelected: () => onDone?.(),
      },
    });
  } catch {
    // The Customer Center failing to open is not worth an alert: nothing was
    // lost, and every route it offers is also reachable from the store's own
    // subscription settings.
  }

  onDone?.();
}

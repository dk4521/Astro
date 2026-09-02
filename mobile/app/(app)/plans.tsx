/**
 * Enuma Sky Pro.
 *
 * **Not a paywall, a price list.** Nothing on this screen is urgent, nothing
 * counts down, and nothing implies that the reader is missing out. The
 * product's whole position is that it does not sell fear, and a pricing screen
 * is where that position is easiest to abandon and most obvious when you do.
 *
 * **What this screen used to be.** A balance, a row of credit packs, and two
 * Razorpay subscriptions — a currency where a message cost one credit. All of
 * it is gone. The ledger behind it was undone by the thing that made it
 * convenient: a client-chosen idempotency key meant one fixed `request_id`,
 * sent forever, was charged exactly once. The replacement is not a better key.
 * A subscription is not a currency, so there is nothing to meter and nothing to
 * replay, and the sentence a reader has to hold in their head went from "how
 * many messages do I have left" to "am I subscribed".
 *
 * **The prices are not here.** They are inside the paywall, which RevenueCat
 * draws from the dashboard using the store's own localised strings — already in
 * the buyer's currency, already carrying whatever introductory offer they
 * personally qualify for. A price written here would be this app's guess at
 * what the store is about to charge, and it would be wrong for everyone
 * travelling and everyone on an offer.
 *
 * **Restore is not optional.** App Review rejects builds that sell a
 * subscription or a lifetime unlock without a visible way to get it back, and
 * the requirement is a real one: a lifetime buyer on a new phone has no other
 * route to what they paid for.
 */

import { useFocusEffect, useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { Platform, ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, ErrorNote, Label } from '../../src/components/ui';
import { useAuth } from '../../src/auth/context';
import { refreshBillingStatus } from '../../src/api/subscription';
import { PRO_ENTITLEMENT } from '../../src/purchases/config';
import { usePurchases } from '../../src/purchases/context';
import { restorePurchases } from '../../src/purchases/client';
import { presentCustomerCenter, presentPaywall } from '../../src/purchases/paywall';
import { colors, radius, space, type } from '../../src/theme';

/** What a subscription covers, and what never needed one. */
const INCLUDED = [
  'Your opening reading, in Hinglish, English or Hindi',
  'Questions about your chart, for as long as you want to ask them',
  'The daily line on the home screen',
  'Reading a tarot spread together',
];

const ALWAYS_FREE = [
  'Your chart, navamsa and house lords',
  'Vimshottari dashas, to three levels',
  'Panchang, today and at birth',
  'Ashtakoot matching',
  'Turning the cards over',
  'The whole course',
];

function Bullets({ items, muted }: { items: string[]; muted?: boolean }) {
  return (
    <View style={styles.bullets}>
      {items.map((item) => (
        <Text key={item} style={muted ? styles.bulletMuted : styles.bullet}>
          •  {item}
        </Text>
      ))}
    </View>
  );
}

function ProSection() {
  const { available, ready, pro, expiresAt, renews, preview, sandbox, refresh } = usePurchases();

  const [busy, setBusy] = useState<'paywall' | 'restore' | 'manage' | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);
  /** Set when the store says Pro and the server disagrees. See `settle` below. */
  const [unverified, setUnverified] = useState(false);

  /**
   * Tell the backend to look again, and notice when it still says no.
   *
   * The server gates on its own reading of the entitlement, not on the SDK's,
   * because a rooted phone can claim anything. So the two can disagree — a
   * purchase that never reached RevenueCat, a `logIn` that did not attach the
   * receipt to this account — and the person that happens to has paid, sees
   * "Active" here, and gets refused every time they ask a question. Without
   * this that is invisible from the inside and reads as theft from the outside.
   */
  const settle = useCallback(async () => {
    const server = await refreshBillingStatus();
    // Null is "could not ask", not "not subscribed". A train tunnel must not
    // raise a warning about somebody's payment.
    setUnverified(server !== null && server.enabled && server.signedIn && !server.pro);
  }, []);

  const open = useCallback(async () => {
    setBusy('paywall');
    setError(null);
    setNote(null);

    const outcome = await presentPaywall();
    // The entitlement reaches the provider through its customer info listener,
    // so this refresh is belt and braces — but the listener can land a frame
    // after the sheet closes, and this screen is the one being looked at.
    await refresh();

    if (outcome.status === 'entitled') {
      setNote(outcome.restored ? 'Restored. Pro is active again.' : 'Pro is active. Thank you.');
      await settle();
    } else if (outcome.status === 'error') {
      setError(outcome.message);
    }

    setBusy(null);
  }, [refresh, settle]);

  const restore = useCallback(async () => {
    setBusy('restore');
    setError(null);
    setNote(null);

    const outcome = await restorePurchases();
    await refresh();

    if (outcome.status === 'error') {
      setError(outcome.message);
    } else {
      // A restore that finds nothing is a success that changed nothing, and
      // saying "restored" would imply something arrived. The entitlement is
      // read back rather than assumed.
      const found = Boolean(outcome.customerInfo.entitlements.active[PRO_ENTITLEMENT]);
      setNote(found ? 'Restored. Pro is active again.' : 'Nothing to restore on this account.');
      if (found) await settle();
    }

    setBusy(null);
  }, [refresh, settle]);

  const manage = useCallback(async () => {
    setBusy('manage');
    await presentCustomerCenter(refresh);
    setBusy(null);
  }, [refresh]);

  /**
   * Clear the last attempt on the way out.
   *
   * This lives under the drawer, which keeps its screens mounted — so a failed
   * "See plans" left its red banner sitting here forever, and the next person to
   * open the price list met an error about something they never did.
   *
   * Cleared on blur rather than on focus, which is what the returned function
   * is. The paywall is a native sheet over this screen, and if it takes focus
   * away and gives it back, a focus-time clear would wipe the very message that
   * attempt is about to write.
   */
  useFocusEffect(
    useCallback(
      () => () => {
        setError(null);
        setNote(null);
      },
      [],
    ),
  );

  // Checked once on open, so a mismatch that happened on another device or on a
  // previous launch is noticed without anyone having to buy anything again.
  useEffect(() => {
    if (ready && pro) void settle();
  }, [ready, pro, settle]);

  if (!available) return null;

  return (
    <View style={styles.section}>
      <Label>Enuma Sky Pro</Label>

      <Card style={pro ? styles.cardCurrent : undefined}>
        {!ready ? (
          <Text style={styles.muted}>Checking your account…</Text>
        ) : pro ? (
          <>
            <Text style={styles.planTitle}>Active</Text>
            <Text style={styles.planSub}>
              {expiresAt === null
                ? 'Bought outright. It does not expire.'
                : renews
                  ? `Renews on ${expiresAt.toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}.`
                  : `Ends on ${expiresAt.toLocaleDateString('en-IN', {
                      day: 'numeric',
                      month: 'long',
                      year: 'numeric',
                    })}. It will not renew.`}
            </Text>
            <View style={styles.action}>
              <Button
                title={busy === 'manage' ? 'Opening…' : 'Manage subscription'}
                onPress={manage}
                disabled={busy !== null}
                loading={busy === 'manage'}
                variant="ghost"
              />
            </View>
          </>
        ) : (
          <>
            <Text style={styles.planTitle}>Weekly, monthly, yearly or once</Text>
            <Text style={styles.planSub}>
              Billed by {Platform.OS === 'ios' ? 'the App Store' : 'Google Play'}. Cancel any time.
            </Text>
            <View style={styles.action}>
              <Button
                title={busy === 'paywall' ? 'Opening…' : 'See plans'}
                onPress={open}
                disabled={busy !== null}
                loading={busy === 'paywall'}
              />
            </View>
            <View style={styles.action}>
              <Button
                title={busy === 'restore' ? 'Restoring…' : 'Restore purchases'}
                onPress={restore}
                disabled={busy !== null}
                loading={busy === 'restore'}
                variant="ghost"
              />
            </View>
          </>
        )}
      </Card>

      {error ? <ErrorNote message={error} /> : null}
      {note ? <Text style={styles.note}>{note}</Text> : null}

      {/* Said plainly, because the alternative is a person who has paid being
          refused with no explanation and no idea who to ask. */}
      {unverified ? (
        <Text style={styles.warn}>
          This phone says Pro is active but the server has not seen it yet. Sign out and back
          in to reattach the purchase.
        </Text>
      ) : null}

      {/* Development only, and worth the space: in Expo Go the paywall draws
          from mocks and in the Test Store a purchase costs nothing, so an
          active entitlement on this screen is not evidence that billing works.
          Someone has to be told that, or it gets shipped. */}
      {preview || sandbox ? (
        <Text style={styles.fine}>
          {preview
            ? 'Expo Go: paywalls are drawn from mock data and nothing can be charged. Use a development build to test a real purchase.'
            : 'Test Store: purchases here are simulated and grant Pro without charging.'}
        </Text>
      ) : null}
    </View>
  );
}

export default function Plans() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, available: accountsAvailable } = useAuth();
  const { available: purchasesAvailable, pro } = usePurchases();

  return (
    <View style={styles.screen}>
      <ScreenHeader
        title="Plans"
        onBack={router.canGoBack() ? () => router.back() : undefined}
      />

      <ScrollView
        contentContainerStyle={[styles.content, { paddingBottom: insets.bottom + space.xxl }]}
        showsVerticalScrollIndicator={false}
      >
        <ProSection />

        {/* Honest rather than hopeful. A "coming soon" that never arrives is
            worse than a sentence that says what is actually true. */}
        {!purchasesAvailable ? (
          <Text style={styles.muted}>Subscriptions are not switched on for this build.</Text>
        ) : null}

        <View style={styles.section}>
          <Label>What Pro covers</Label>
          <Card>
            <Bullets items={INCLUDED} />
          </Card>
        </View>

        <View style={styles.section}>
          <Label>Free, and staying that way</Label>
          <Card>
            <Bullets items={ALWAYS_FREE} muted />
          </Card>
        </View>

        {!user && accountsAvailable && !pro ? (
          <View style={styles.section}>
            <Text style={styles.note}>A subscription follows your account to a new phone.</Text>
            <View style={styles.action}>
              <Button title="Sign in" onPress={() => router.push('/sign-in')} tone="signIn" />
            </View>
          </View>
        ) : null}

      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { paddingHorizontal: space.md, paddingTop: space.md, gap: space.lg },
  section: { gap: space.sm },

  cardCurrent: { borderColor: colors.accent },

  planTitle: { ...type.heading, color: colors.text },
  planSub: { ...type.body, color: colors.textMuted, marginTop: 2 },

  bullets: { gap: space.xs },
  bullet: { ...type.body, color: colors.text, lineHeight: 21 },
  bulletMuted: { ...type.body, color: colors.textMuted, lineHeight: 21 },

  action: { marginTop: space.md },

  note: { ...type.body, fontSize: 13, color: colors.textMuted, lineHeight: 19, marginTop: space.sm },
  muted: { ...type.body, color: colors.textMuted },
  warn: { ...type.body, fontSize: 13, color: colors.accent, lineHeight: 19 },
  fine: {
    ...type.body,
    fontSize: 12,
    color: colors.textFaint,
    lineHeight: 18,
    marginTop: space.md,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.glassBorder,
    paddingTop: space.md,
    borderRadius: radius.sm,
  },
});

/**
 * What messages cost.
 *
 * **Not a paywall, a price list.** Nothing on this screen is urgent, nothing
 * counts down, and nothing implies that the reader is missing out on
 * something. The product's whole position is that it does not sell fear, and a
 * pricing screen is where that position is easiest to abandon and most obvious
 * when you do.
 *
 * **The prices are fetched, not bundled.** A store build from six months ago
 * still draws today's numbers, and cannot draw one the server would refuse to
 * charge. Which also means this screen has three empty states worth handling
 * separately: still loading, nothing configured to sell, and no account yet.
 *
 * **Packs are shown after subscriptions and are not apologised for.** Their
 * per-message price is roughly ten times a subscription's, which is the honest
 * shape of the thing: a pack buys occasional use without a commitment, and the
 * screen says exactly that rather than hiding the arithmetic.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { ScrollView, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, ErrorNote, Label } from '../../src/components/ui';
import { useAuth } from '../../src/auth/context';
import { loadAllowance, type Allowance } from '../../src/api/allowance';
import {
  cancelSubscription,
  checkout,
  fetchPlans,
  type BillingPlan,
  type Catalogue,
} from '../../src/api/billing';
import { colors, radius, space, type } from '../../src/theme';

/** Enough to say what a month costs per message without a calculator. */
function perMessage(plan: BillingPlan): string {
  const paise = plan.amount_paise / plan.credits;
  return paise >= 100 ? `₹${(paise / 100).toFixed(2)} a message` : `${Math.round(paise)}p a message`;
}

function PlanCard({
  plan,
  busy,
  disabled,
  current,
  onChoose,
}: {
  plan: BillingPlan;
  busy: boolean;
  disabled: boolean;
  current: boolean;
  onChoose: () => void;
}) {
  const subscription = plan.kind === 'subscription';

  return (
    <Card style={current ? styles.cardCurrent : undefined}>
      <View style={styles.head}>
        <View style={styles.headText}>
          <Text style={styles.planTitle}>
            {subscription ? plan.label : plan.label}
          </Text>
          <Text style={styles.planSub}>
            {subscription
              ? `${plan.credits.toLocaleString('en-IN')} messages a month`
              : plan.validity_days
                ? `Valid for ${Math.round(plan.validity_days / 30)} months`
                : 'No expiry'}
          </Text>
        </View>
        <View style={styles.priceGroup}>
          <Text style={styles.price}>₹{plan.rupees}</Text>
          <Text style={styles.priceHint}>
            {plan.period === 'monthly' ? 'a month' : plan.period === 'yearly' ? 'a year' : 'once'}
          </Text>
        </View>
      </View>

      <Text style={styles.perMessage}>{perMessage(plan)}</Text>

      {/* Yearly's only argument is the division, so the screen does it. */}
      {plan.period === 'yearly' ? (
        <Text style={styles.perMessage}>
          ₹{Math.round(plan.amount_paise / 1200)} a month, paid once
        </Text>
      ) : null}

      <View style={styles.action}>
        <Button
          title={current ? 'Current plan' : busy ? 'Opening…' : 'Choose'}
          onPress={onChoose}
          disabled={disabled || current}
          loading={busy}
          variant={subscription ? 'primary' : 'ghost'}
        />
      </View>
    </Card>
  );
}

export default function Plans() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { user, available } = useAuth();

  const [catalogue, setCatalogue] = useState<Catalogue | null>(null);
  const [allowance, setAllowance] = useState<Allowance | null>(null);
  const [busy, setBusy] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [note, setNote] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    setAllowance(await loadAllowance(user?.id ?? null));
  }, [user]);

  useEffect(() => {
    let cancelled = false;

    fetchPlans()
      .then((loaded) => !cancelled && setCatalogue(loaded))
      .catch(() => !cancelled && setCatalogue({ enabled: false, currency: 'INR', plans: [] }));

    void refresh();
    return () => {
      cancelled = true;
    };
  }, [refresh]);

  const buy = useCallback(
    async (plan: BillingPlan) => {
      if (!user) {
        router.push('/sign-in');
        return;
      }

      setBusy(plan.id);
      setError(null);
      setNote(null);

      try {
        const outcome = await checkout(plan.id, async () => {
          const fresh = await loadAllowance(user.id);
          return fresh.balance;
        });

        await refresh();

        if (outcome === 'paid') {
          setNote('Added. They are on your account now.');
        } else if (outcome === 'pending') {
          // The webhook is the source of truth and Razorpay retries it, so a
          // payment that went through will land. Saying "failed" here would be
          // a lie told to someone who has just been charged.
          setNote('Payment received. Credits can take a minute to appear — pull back in shortly.');
        }
      } catch (caught) {
        setError(caught instanceof Error ? caught.message : 'Could not open checkout.');
      } finally {
        setBusy(null);
      }
    },
    [user, router, refresh],
  );

  const stop = useCallback(async () => {
    setBusy('cancel');
    setError(null);
    try {
      setNote(await cancelSubscription());
      await refresh();
    } catch (caught) {
      setError(caught instanceof Error ? caught.message : 'Could not cancel.');
    } finally {
      setBusy(null);
    }
  }, [refresh]);

  const subscriptions = catalogue?.plans.filter((p) => p.kind === 'subscription') ?? [];
  const packs = catalogue?.plans.filter((p) => p.kind === 'pack') ?? [];
  const subscribed = allowance?.plan !== 'free' && allowance?.status === 'active';

  return (
    <View style={styles.screen}>
      <ScreenHeader title="Messages" onBack={() => router.back()} />

      <ScrollView
        contentContainerStyle={[styles.content, { paddingBottom: insets.bottom + space.xxl }]}
        showsVerticalScrollIndicator={false}
      >
        {/* The balance leads, because it is the only number on this screen the
            reader did not come here to be sold. */}
        {user ? (
          <View style={styles.section}>
            <Label>Your balance</Label>
            <Card>
              <Text style={styles.balance}>
                {allowance ? allowance.balance.toLocaleString('en-IN') : '—'}
              </Text>
              <Text style={styles.balanceHint}>
                {allowance?.plan === 'free'
                  ? 'Six free messages arrive every morning.'
                  : `On the ${allowance?.plan} plan.`}
              </Text>
            </Card>
          </View>
        ) : null}

        {error ? <ErrorNote message={error} /> : null}
        {note ? <Text style={styles.note}>{note}</Text> : null}

        {catalogue === null ? (
          <Text style={styles.muted}>Loading prices…</Text>
        ) : !catalogue.enabled ? (
          // Honest rather than hopeful. A "coming soon" that never arrives is
          // worse than a sentence that says what is actually true.
          <Text style={styles.muted}>
            Buying messages is not switched on for this build. The six free ones
            a day work as usual.
          </Text>
        ) : (
          <>
            {subscriptions.length ? (
              <View style={styles.section}>
                <Label>Every month</Label>
                {subscriptions.map((plan) => (
                  <PlanCard
                    key={plan.id}
                    plan={plan}
                    busy={busy === plan.id}
                    disabled={busy !== null}
                    current={subscribed === true && allowance?.plan === plan.period}
                    onChoose={() => buy(plan)}
                  />
                ))}
              </View>
            ) : null}

            {packs.length ? (
              <View style={styles.section}>
                <Label>Or pay as you go</Label>
                {packs.map((plan) => (
                  <PlanCard
                    key={plan.id}
                    plan={plan}
                    busy={busy === plan.id}
                    disabled={busy !== null}
                    current={false}
                    onChoose={() => buy(plan)}
                  />
                ))}
                <Text style={styles.note}>
                  Packs cost more per message than a plan does. They are for
                  asking now and again without signing up for anything.
                </Text>
              </View>
            ) : null}

            {subscribed ? (
              <View style={styles.section}>
                <Label>Your plan</Label>
                <Text style={styles.note}>
                  {allowance?.periodEnd
                    ? `Paid up to ${allowance.periodEnd.toLocaleDateString('en-IN', {
                        day: 'numeric',
                        month: 'long',
                        year: 'numeric',
                      })}.`
                    : 'Renews automatically.'}
                </Text>
                <View style={styles.action}>
                  <Button
                    title={busy === 'cancel' ? 'Cancelling…' : 'Cancel plan'}
                    onPress={stop}
                    disabled={busy !== null}
                    loading={busy === 'cancel'}
                    variant="ghost"
                  />
                </View>
                <Text style={styles.note}>
                  Cancelling stops the next payment. Everything you have already
                  paid for stays yours until the period ends.
                </Text>
              </View>
            ) : null}
          </>
        )}

        {!user && available ? (
          <View style={styles.section}>
            <Text style={styles.note}>
              Messages are counted against an account, so they follow you to a
              new phone.
            </Text>
            <View style={styles.action}>
              <Button title="Sign in" onPress={() => router.push('/sign-in')} tone="signIn" />
            </View>
          </View>
        ) : null}

        <Text style={styles.fine}>
          One credit is one message. Free credits are used before paid ones, so
          nothing you have bought is spent while today's are still there.
        </Text>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  screen: { flex: 1 },
  content: { paddingHorizontal: space.md, paddingTop: space.md, gap: space.lg },
  section: { gap: space.sm },

  cardCurrent: { borderColor: colors.accent },

  head: { flexDirection: 'row', alignItems: 'flex-start', justifyContent: 'space-between' },
  headText: { flex: 1, paddingRight: space.md },
  planTitle: { ...type.heading, color: colors.text },
  planSub: { ...type.body, color: colors.textMuted, marginTop: 2 },

  priceGroup: { alignItems: 'flex-end' },
  price: { ...type.title, color: colors.text },
  priceHint: { ...type.body, fontSize: 12, color: colors.textFaint },

  perMessage: { ...type.body, fontSize: 13, color: colors.textFaint, marginTop: space.xs },

  action: { marginTop: space.md },

  balance: { ...type.display, color: colors.text },
  balanceHint: { ...type.body, color: colors.textMuted, marginTop: space.xs },

  note: { ...type.body, fontSize: 13, color: colors.textMuted, lineHeight: 19 },
  muted: { ...type.body, color: colors.textMuted },
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

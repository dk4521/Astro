/**
 * Settings.
 *
 * Small on purpose. It exists because changing birth details was buried at the
 * bottom of the chart screen, where a user who mistyped their birth time had to
 * scroll past the consequences of that mistake to fix it.
 *
 * The screen is a sheet of glass over the night sky: the cards are translucent
 * and the background is `StarField`, not a flat fill. Nothing here explains
 * itself in prose any more — a row that needs a paragraph under it is a row
 * that was named badly.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, TextInput, View } from 'react-native';

import { useAuth } from '../../src/auth/context';
import { useSync } from '../../src/sync/context';
import { clearChartCaches } from '../../src/api/cache';
import {
  clearBirthDetails,
  clearProgress,
  loadBirthDetails,
  loadName,
  loadProgress,
  saveName,
} from '../../src/api/storage';
import { API_NOT_CONFIGURED } from '../../src/api/client';
import { loadAllowance, type Allowance } from '../../src/api/allowance';
import type { BirthDetails } from '../../src/api/types';
import { toDisplayDate } from '../../src/format';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, ErrorNote, Label, Row } from '../../src/components/ui';
import { colors, radius, space, type } from '../../src/theme';

/** "just now", "6 min ago" — enough to tell fresh from stuck. */
function sinceText(at: number | null): string {
  if (!at) return 'not yet';
  const minutes = Math.floor((Date.now() - at) / 60000);
  if (minutes < 1) return 'just now';
  if (minutes < 60) return `${minutes} min ago`;
  const hours = Math.floor(minutes / 60);
  if (hours < 24) return `${hours} h ago`;
  return `${Math.floor(hours / 24)} d ago`;
}

const PLAN_LABEL: Record<'free' | 'monthly' | 'yearly', string> = {
  free: 'Free',
  monthly: 'Monthly',
  yearly: 'Yearly',
};

/**
 * When the soonest-expiring credits go.
 *
 * Almost always tonight — the free six expire at midnight — so the common case
 * is a word rather than a date. A date here would be technically correct and
 * would read as a warning about something that happens every single day.
 */
function expiryPhrase(at: Date): string {
  const hours = (at.getTime() - Date.now()) / 3_600_000;
  if (hours <= 24) return 'tonight';
  if (hours <= 48) return 'tomorrow';
  return `on ${at.toLocaleDateString('en-IN', { day: 'numeric', month: 'short' })}`;
}

export default function Settings() {
  const router = useRouter();
  const { available, user, signOut } = useAuth();
  const {
    enabled: syncing,
    status,
    lastSyncedAt,
    error: syncError,
    syncNow,
    pushProgressReset,
    clearChatHistory,
  } = useSync();
  const [details, setDetails] = useState<BirthDetails | null>(null);
  const [readCount, setReadCount] = useState(0);
  const [name, setName] = useState('');
  const [allowance, setAllowance] = useState<Allowance | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadAllowance(user?.id ?? null).then((next) => {
      if (!cancelled) setAllowance(next);
    });
    return () => {
      cancelled = true;
    };
  }, [user]);

  useEffect(() => {
    let cancelled = false;
    Promise.all([loadBirthDetails(), loadProgress(), loadName()]).then(
      ([saved, progress, storedName]) => {
      if (cancelled) return;
      setDetails(saved);
      setReadCount(progress.length);
      setName(storedName);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  const changeBirth = useCallback(async () => {
    // The cached chapters and the cached reading were both computed from the
    // old chart, so they go with it.
    await Promise.all([clearBirthDetails(), clearChartCaches()]);
    router.replace('/onboarding');
  }, [router]);

  const resetCourse = useCallback(() => {
    Alert.alert(
      'Reset course progress?',
      'The chapters stay; only the ticks are cleared.',
      [
        { text: 'Cancel', style: 'cancel' },
        {
          text: 'Reset',
          style: 'destructive',
          onPress: async () => {
            await clearProgress();
            // Explicitly, because a union merge cannot express a deletion: left
            // upstream, every tick would come back on the next sync.
            await pushProgressReset();
            setReadCount(0);
          },
        },
      ],
    );
  }, [pushProgressReset]);

  const forgetChat = useCallback(() => {
    Alert.alert(
      'Delete chat history?',
      'Every question and answer stored in your account is removed. This cannot be undone.',
      [
        { text: 'Cancel', style: 'cancel' },
        { text: 'Delete', style: 'destructive', onPress: () => clearChatHistory() },
      ],
    );
  }, [clearChatHistory]);

  return (
    <View style={styles.flex}>
      <ScreenHeader title="Settings" bordered={false} />

      <ScrollView contentContainerStyle={styles.content}>
        {/* Renders nothing in a correctly built app. It survives the prose cull
            because without it a build with no API URL fails as anonymous
            network timeouts on every screen. */}
        {API_NOT_CONFIGURED ? (
          <View style={styles.section}>
            <ErrorNote message="This build has no API address, so nothing served from the backend can load." />
          </View>
        ) : null}

        <View style={styles.section}>
          <Label>Account</Label>
          <Card>
            {!available ? (
              <Text style={styles.empty}>Accounts are not configured in this build.</Text>
            ) : user ? (
              <>
                <Row label="Signed in as" value={user.email ?? 'this account'} />
                <Row
                  label="Sync"
                  value={status === 'error' ? 'Failed' : status === 'syncing' ? 'Syncing…' : 'On'}
                  hint={
                    status === 'error'
                      ? (syncError ?? 'Could not reach your account.')
                      : `Last synced ${sinceText(lastSyncedAt)}`
                  }
                />
              </>
            ) : (
              <Text style={styles.empty}>Not signed in.</Text>
            )}
          </Card>
          {available ? (
            <View style={styles.action}>
              {user ? (
                <>
                  <Button
                    title="Sync now"
                    onPress={syncNow}
                    variant="ghost"
                    loading={status === 'syncing'}
                  />
                  <View style={styles.action}>
                    <Button title="Sign out" onPress={signOut} tone="signOut" />
                  </View>
                </>
              ) : (
                <Button
                  title="Sign in or create an account"
                  onPress={() => router.push('/sign-in')}
                  tone="signIn"
                />
              )}
            </View>
          ) : null}
        </View>

        {/* Here as well as in onboarding, because everyone who installed the
            app before the field existed has never been asked. */}
        <View style={styles.section}>
          <Label>Your name</Label>
          <TextInput
            style={styles.nameInput}
            value={name}
            onChangeText={setName}
            onEndEditing={() => saveName(name)}
            onBlur={() => saveName(name)}
            placeholder="Optional"
            placeholderTextColor={colors.textFaint}
            autoCorrect={false}
            maxLength={40}
          />
        </View>

        <View style={styles.section}>
          <Label>Birth details</Label>
          <Card>
            {details ? (
              <>
                <Row label="Date" value={toDisplayDate(details.date)} />
                <Row label="Time" value={details.time} />
                <Row
                  label="Place"
                  value={details.place ?? '—'}
                  hint={`${details.latitude.toFixed(4)}°, ${details.longitude.toFixed(4)}°`}
                />
              </>
            ) : (
              <Text style={styles.empty}>Nothing saved yet.</Text>
            )}
          </Card>
          <View style={styles.action}>
            <Button title="Change birth details" onPress={changeBirth} variant="ghost" />
          </View>
        </View>

        {/* A summary, not a price list. Anything that costs money lives on
            /plans, so this screen stays a place to check facts rather than a
            second place to be sold to. */}
        {user ? (
          <View style={styles.section}>
            <Label>Messages</Label>
            <Card>
              <Row
                label="Plan"
                value={PLAN_LABEL[allowance?.plan ?? 'free']}
                hint={
                  allowance && allowance.plan !== 'free' && allowance.status
                    ? allowance.status
                    : 'Six free messages a day'
                }
              />
              <Row
                label="Balance"
                value={allowance ? String(allowance.balance) : '—'}
                hint={
                  allowance?.expiresAt
                    ? `Some expire ${expiryPhrase(allowance.expiresAt)}`
                    : undefined
                }
              />
            </Card>
            <View style={styles.action}>
              <Button title="See plans" onPress={() => router.push('/plans')} variant="ghost" />
            </View>
          </View>
        ) : null}

        <View style={styles.section}>
          <Label>Course</Label>
          <Card>
            <Row label="Chapters read" value={`${readCount} of 30`} />
          </Card>
          <View style={styles.action}>
            <Button title="Reset progress" onPress={resetCourse} variant="ghost" />
          </View>
        </View>

        {syncing ? (
          <View style={styles.section}>
            <Label>Chat history</Label>
            <Card>
              <Row label="Stored" value="In your account" />
            </Card>
            <View style={styles.action}>
              <Button title="Delete chat history" onPress={forgetChat} variant="ghost" />
            </View>
          </View>
        ) : null}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  // No background colour: StarField is the background, and a fill here would
  // sit on top of it.
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  section: { marginBottom: space.xl },
  empty: { ...type.body, color: colors.textMuted },
  action: { marginTop: space.md },
  note: { ...type.mono, color: colors.textFaint, marginTop: space.sm, lineHeight: 18 },
  nameInput: {
    ...type.body,
    color: colors.text,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingVertical: space.sm + 2,
    marginTop: space.sm,
  },
});

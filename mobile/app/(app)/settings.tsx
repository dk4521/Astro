/**
 * Settings.
 *
 * Small on purpose. It exists because changing birth details was buried at the
 * bottom of the chart screen, where a user who mistyped their birth time had to
 * scroll past the consequences of that mistake to fix it.
 *
 * It is also the only place that answers "where is my data". That section names
 * every store by what actually holds it, including a sync that has failed —
 * telling someone their chart is safe in an account it never reached is the one
 * lie a settings screen must not tell.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '../../src/auth/context';
import { useSync } from '../../src/sync/context';
import { clearChartCaches } from '../../src/api/cache';
import { clearBirthDetails, clearProgress, loadBirthDetails, loadProgress } from '../../src/api/storage';
import { API_BASE_URL, API_NOT_CONFIGURED } from '../../src/api/client';
import type { BirthDetails } from '../../src/api/types';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, Label, Row } from '../../src/components/ui';
import { colors, space, type } from '../../src/theme';

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

  useEffect(() => {
    let cancelled = false;
    Promise.all([loadBirthDetails(), loadProgress()]).then(([saved, progress]) => {
      if (cancelled) return;
      setDetails(saved);
      setReadCount(progress.length);
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
      <ScreenHeader title="Settings" />

      <ScrollView contentContainerStyle={styles.content}>
        <View style={styles.section}>
          <Label>Account</Label>
          <Card>
            {!available ? (
              <Text style={styles.empty}>
                Accounts are not configured in this build.
              </Text>
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
          <Text style={styles.note}>
            Signing in is optional. An account carries your chart, chat history
            and course progress to a new phone; without one everything still
            works and stays on this device.
          </Text>
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
                    <Button title="Sign out" onPress={signOut} variant="ghost" />
                  </View>
                </>
              ) : (
                <Button
                  title="Sign in or create an account"
                  onPress={() => router.push('/sign-in')}
                  variant="ghost"
                />
              )}
            </View>
          ) : null}
          {syncing ? (
            <Text style={styles.note}>
              Signing out leaves your chart and progress on this phone. Nothing
              is deleted from the account either — signing back in brings both
              copies together.
            </Text>
          ) : null}
        </View>

        <View style={styles.section}>
          <Label>Birth details</Label>
          <Card>
            {details ? (
              <>
                <Row label="Date" value={details.date} />
                <Row label="Time" value={details.time} />
                <Row label="Place" value={details.place ?? '—'}
                  hint={`${details.latitude.toFixed(4)}°, ${details.longitude.toFixed(4)}°`} />
              </>
            ) : (
              <Text style={styles.empty}>Nothing saved yet.</Text>
            )}
          </Card>
          <Text style={styles.note}>
            These three facts decide every number in the app. Changing them casts a
            new chart from scratch.
          </Text>
          <View style={styles.action}>
            <Button title="Change birth details" onPress={changeBirth} variant="ghost" />
          </View>
        </View>

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
              <Row
                label="Stored"
                value="In your account"
                hint="Questions, answers, and whether each answer matched your chart"
              />
            </Card>
            <View style={styles.action}>
              <Button title="Delete chat history" onPress={forgetChat} variant="ghost" />
            </View>
          </View>
        ) : null}

        <View style={styles.section}>
          <Label>Where your data lives</Label>
          <Card>
            <Row
              label="Birth details"
              value={syncing ? 'This device and your account' : 'This device only'}
            />
            <Row
              label="Course progress"
              value={syncing ? 'This device and your account' : 'This device only'}
            />
            <Row label="Course text" value="Downloaded, then cached" />
            <Row
              label="Your reading"
              value="Kept for the day"
              hint="Generating one costs a model request, so the same chart and language is not asked twice in a day"
            />
            <Row label="Chat history" value={syncing ? 'Your account' : 'Not stored'} />
            <Row label="Account" value={user ? 'Signed in' : 'None'} />
            <Row
              label="API"
              value={API_BASE_URL}
              hint={
                API_NOT_CONFIGURED
                  ? 'This build has no EXPO_PUBLIC_API_URL, so it is pointing at the phone itself. Nothing served from the backend can work until it is rebuilt with one.'
                  : undefined
              }
            />
          </Card>
          <Text style={styles.note}>
            {syncing
              ? status === 'error'
                ? 'The last sync did not reach your account, so the rows above may still be device-only. Everything is safe on this phone and will go up on the next successful sync.'
                : 'Your birth details are sent to the API to compute a chart and are not retained there. What is stored in your account is stored under row-level security: only your own session can read it.'
              : 'Nothing leaves this phone except the birth details sent to the API to compute a chart, which are not retained there.'}
          </Text>
        </View>
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  section: { marginBottom: space.xl },
  empty: { ...type.body, color: colors.textMuted },
  note: { ...type.mono, color: colors.textFaint, marginTop: space.sm, lineHeight: 18 },
  action: { marginTop: space.md },
});

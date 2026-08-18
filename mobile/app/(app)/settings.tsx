/**
 * Settings.
 *
 * Small on purpose. It exists because changing birth details was buried at the
 * bottom of the chart screen, where a user who mistyped their birth time had to
 * scroll past the consequences of that mistake to fix it.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useState } from 'react';
import { Alert, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useAuth } from '../../src/auth/context';
import { clearCourseCache } from '../../src/api/course';
import { clearBirthDetails, clearProgress, loadBirthDetails, loadProgress } from '../../src/api/storage';
import { API_BASE_URL } from '../../src/api/client';
import type { BirthDetails } from '../../src/api/types';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, Card, Label, Row } from '../../src/components/ui';
import { colors, space, type } from '../../src/theme';

export default function Settings() {
  const router = useRouter();
  const { available, user, signOut } = useAuth();
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
    // Cached chapters carry a line computed from the old chart, so they go too.
    await Promise.all([clearBirthDetails(), clearCourseCache()]);
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
            setReadCount(0);
          },
        },
      ],
    );
  }, []);

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
              <Row label="Signed in as" value={user.email ?? 'this account'} />
            ) : (
              <Text style={styles.empty}>Not signed in.</Text>
            )}
          </Card>
          <Text style={styles.note}>
            Signing in is optional. Nothing syncs yet — an account is what will
            carry your chart, chat history and course progress to a new phone.
          </Text>
          {available ? (
            <View style={styles.action}>
              {user ? (
                <Button title="Sign out" onPress={signOut} variant="ghost" />
              ) : (
                <Button
                  title="Sign in or create an account"
                  onPress={() => router.push('/sign-in')}
                  variant="ghost"
                />
              )}
            </View>
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

        <View style={styles.section}>
          <Label>Where your data lives</Label>
          <Card>
            <Row label="Birth details" value="This device only" />
            <Row label="Course progress" value="This device only" />
            <Row label="Course text" value="Downloaded, then cached" />
            <Row label="Chat history" value="Not stored" />
            <Row label="Account" value={user ? 'Signed in' : 'None'} />
            <Row label="API" value={API_BASE_URL} />
          </Card>
          <Text style={styles.note}>
            Nothing is uploaded to an account, because there are no accounts yet.
            Your birth details are sent to the API to compute a chart and are not
            retained there.
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

/**
 * Root navigation.
 *
 * Two branches, deliberately separate: onboarding is a screen you pass through
 * once, and `(app)` is everything you live in afterwards. Keeping onboarding
 * outside the drawer means there is no sidebar to open — and nothing to
 * navigate to — before the app knows when and where you were born.
 */

import { Stack } from 'expo-router';
import { StatusBar } from 'expo-status-bar';
import { useEffect, useState } from 'react';
import { View } from 'react-native';
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { migrateLegacyKeys } from '../src/api/migrate';
import { AuthProvider } from '../src/auth/context';
import { StarField } from '../src/components/StarField';
import { PurchasesProvider } from '../src/purchases/context';
import { SyncProvider } from '../src/sync/context';
import { colors } from '../src/theme';


export default function RootLayout() {
  // The app's old storage keys, moved to the new name before anything can read
  // the new ones — see `src/api/migrate.ts`. It has to finish rather than race:
  // `SyncProvider` reads the birth details the moment it mounts, and finding
  // none there would push an empty device up to a full account.
  //
  // One `getAllKeys` on an install with nothing to move, so the wait is a frame
  // rather than a delay — and it is spent on the splash colour, not on white.
  const [migrated, setMigrated] = useState(false);
  useEffect(() => {
    void migrateLegacyKeys().finally(() => setMigrated(true));
  }, []);

  if (!migrated) return <View style={{ flex: 1, backgroundColor: colors.bg }} />;

  return (
    // The drawer inside `(app)` is gesture-driven, and gestures need this at
    // the very root or the sidebar simply never opens by swipe.
    <GestureHandlerRootView style={{ flex: 1 }}>
      <SafeAreaProvider>
        <StatusBar style="light" />
        <AuthProvider>
          {/* Inside AuthProvider because it mirrors whoever is signed in, and
              above the routes because `index` waits on its first pass. */}
          <SyncProvider>
            {/* Also inside AuthProvider, and for a sharper reason than Sync: it
                calls `Purchases.logIn` with the Supabase user id, so it cannot
                mount above the thing that knows the id. Above the routes
                because a gate that mounts per-screen would reconfigure the SDK
                on every navigation. */}
            <PurchasesProvider>
              {/* One field for the whole app, mounted above the navigator rather
                  than inside each screen. Per-screen instances would restart the
                  twinkle on every navigation — the sky would visibly blink — and
                  would pay for the animation as many times over as there are
                  screens on the stack. */}
              <StarField />
              <Stack
                screenOptions={{
                  headerShown: false,
                  // Transparent, so the field above shows through every route.
                  contentStyle: { backgroundColor: 'transparent' },
                  animation: 'fade',
                }}
              />
            </PurchasesProvider>
          </SyncProvider>
        </AuthProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

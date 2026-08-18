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
import { GestureHandlerRootView } from 'react-native-gesture-handler';
import { SafeAreaProvider } from 'react-native-safe-area-context';

import { AuthProvider } from '../src/auth/context';
import { SyncProvider } from '../src/sync/context';
import { colors } from '../src/theme';

export default function RootLayout() {
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
            <Stack
              screenOptions={{
                headerShown: false,
                contentStyle: { backgroundColor: colors.bg },
                animation: 'fade',
              }}
            />
          </SyncProvider>
        </AuthProvider>
      </SafeAreaProvider>
    </GestureHandlerRootView>
  );
}

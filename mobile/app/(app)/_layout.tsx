/**
 * The sidebar.
 *
 * `expo-router/drawer` rather than a hand-rolled panel: SDK 57 vendors
 * react-navigation's drawer, so this costs no new dependency and brings the
 * swipe gesture, the back-button handling and the accessibility semantics that
 * a custom overlay would have to reimplement badly.
 *
 * The content is custom, though. The stock drawer is a white list of labels;
 * this one carries the chart summary at the top, because the first question a
 * user has in a sidebar is "whose chart am I looking at".
 */

import { Drawer } from 'expo-router/drawer';
import { DrawerContentScrollView } from 'expo-router/drawer';
import { usePathname, useRouter } from 'expo-router';
import { useEffect, useState } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { useAuth } from '../../src/auth/context';
import { loadBirthDetails } from '../../src/api/storage';
import type { BirthDetails } from '../../src/api/types';
import { colors, radius, space, type } from '../../src/theme';

type Item = {
  route: string;
  label: string;
  hint: string;
  glyph: string;
};

const ITEMS: Item[] = [
  { route: '/today', label: 'Today', hint: 'Panchang now, and your period', glyph: '☉' },
  { route: '/chart', label: 'Chart', hint: 'Your computed kundli', glyph: '◈' },
  { route: '/reading', label: 'Reading', hint: 'Explained, and ask anything', glyph: '❋' },
  { route: '/learn', label: 'Learn', hint: 'A course, using your chart', glyph: '✦' },
  { route: '/settings', label: 'Settings', hint: 'Birth details and data', glyph: '⚙' },
];

function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const insets = useSafeAreaInsets();
  const { user } = useAuth();
  const [details, setDetails] = useState<BirthDetails | null>(null);

  useEffect(() => {
    let cancelled = false;
    loadBirthDetails().then((saved) => {
      if (!cancelled) setDetails(saved);
    });
    return () => {
      cancelled = true;
    };
  }, []);

  return (
    <DrawerContentScrollView
      contentContainerStyle={[styles.sidebar, { paddingTop: insets.top + space.lg }]}
      style={styles.sidebarBg}
    >
      <Text style={styles.brand}>KOSMIQ</Text>
      <Text style={styles.brandLine}>
        {details?.place ?? 'Your chart'}
      </Text>
      {details ? (
        <Text style={styles.brandMeta}>
          {details.date} · {details.time}
        </Text>
      ) : null}
      {user?.email ? <Text style={styles.brandAccount}>{user.email}</Text> : null}

      <View style={styles.items}>
        {ITEMS.map((item) => {
          // `/learn/nakshatras` should still light up the Learn row.
          const active = pathname === item.route || pathname.startsWith(`${item.route}/`);
          return (
            <Pressable
              key={item.route}
              accessibilityRole="button"
              accessibilityState={{ selected: active }}
              onPress={() => router.navigate(item.route as never)}
              style={({ pressed }) => [
                styles.item,
                active && styles.itemActive,
                pressed && styles.itemPressed,
              ]}
            >
              <Text style={[styles.glyph, active && styles.glyphActive]}>{item.glyph}</Text>
              <View style={styles.itemText}>
                <Text style={[styles.itemLabel, active && styles.itemLabelActive]}>
                  {item.label}
                </Text>
                <Text style={styles.itemHint}>{item.hint}</Text>
              </View>
            </Pressable>
          );
        })}
      </View>

      <Text style={styles.footer}>
        Every number in this app is computed from your birth moment. The language
        layer explains it and never calculates it.
      </Text>
    </DrawerContentScrollView>
  );
}

export default function AppLayout() {
  return (
    <Drawer
      drawerContent={() => <Sidebar />}
      screenOptions={{
        headerShown: false,
        drawerType: 'front',
        drawerStyle: { backgroundColor: colors.surface, width: 300 },
        overlayColor: 'rgba(11, 10, 20, 0.6)',
        sceneStyle: { backgroundColor: colors.bg },
      }}
    />
  );
}

const styles = StyleSheet.create({
  sidebarBg: { backgroundColor: colors.surface },
  sidebar: { paddingHorizontal: space.md, paddingBottom: space.xl },
  brand: { ...type.label, color: colors.accent },
  brandLine: { ...type.heading, color: colors.text, marginTop: space.sm },
  brandMeta: { ...type.mono, color: colors.textFaint, marginTop: 2 },
  brandAccount: { ...type.mono, color: colors.accentSoft, marginTop: space.xs },
  items: { marginTop: space.xl, gap: space.xs },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.md,
    paddingVertical: space.md,
    paddingHorizontal: space.md,
    borderRadius: radius.sm,
  },
  itemActive: { backgroundColor: colors.accentDim },
  itemPressed: { opacity: 0.7 },
  glyph: { fontSize: 16, color: colors.textFaint, width: 20, textAlign: 'center' },
  glyphActive: { color: colors.accentSoft },
  itemText: { flex: 1 },
  itemLabel: { ...type.body, color: colors.textMuted, fontWeight: '600' },
  itemLabelActive: { color: colors.text },
  itemHint: { ...type.mono, color: colors.textFaint, marginTop: 2 },
  footer: {
    ...type.mono,
    color: colors.textFaint,
    marginTop: space.xxl,
    lineHeight: 18,
  },
});

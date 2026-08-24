/**
 * The sidebar.
 *
 * `expo-router/drawer` rather than a hand-rolled panel: SDK 57 vendors
 * react-navigation's drawer, so this costs no new dependency and brings the
 * swipe gesture, the back-button handling and the accessibility semantics that
 * a custom overlay would have to reimplement badly.
 *
 * The panel itself is glass: the drawer's own background is transparent and the
 * colour comes from a translucent gradient inside it, so the screen you came
 * from stays faintly visible underneath. The list is destination names and
 * nothing else — a sidebar is for getting somewhere, and every extra line of
 * prose in it is read once and then skipped forever.
 */

import { LinearGradient } from 'expo-linear-gradient';
import { Drawer } from 'expo-router/drawer';
import { DrawerContentScrollView } from 'expo-router/drawer';
import { usePathname, useRouter } from 'expo-router';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';
import Svg, { Path } from 'react-native-svg';

import { useAuth } from '../../src/auth/context';
import { colors, radius, space, type } from '../../src/theme';

type Item = {
  route: string;
  label: string;
  glyph: string;
  accountOnly?: boolean;
};

const ITEMS: Item[] = [
  { route: '/today', label: 'Today', glyph: '☉' },
  { route: '/chart', label: 'Chart', glyph: '◈' },
  { route: '/matching', label: 'Matching', glyph: '◎' },
  // A crescent rather than a card suit: ♠ reads as poker, and the stock
  // Android font is missing enough of the prettier symbols that the power
  // glyph in this very sidebar once shipped as an empty box.
  { route: '/tarot', label: 'Tarot', glyph: '☾' },
  { route: '/reading', label: 'Chat', glyph: '❋' },
  // Only with an account: a signed-out phone keeps no conversations at all, so
  // the row would lead to a permanently empty screen.
  { route: '/history', label: 'History', glyph: '↺', accountOnly: true },
  { route: '/learn', label: 'Learn', glyph: '✦' },
  { route: '/settings', label: 'Settings', glyph: '⚙' },
];

function PowerIcon({ color }: { color: string }) {
  return (
    <Svg width={15} height={15} viewBox="0 0 24 24" fill="none">
      <Path d="M12 2.8 V11" stroke={color} strokeWidth={2.4} strokeLinecap="round" />
      <Path
        d="M6.6 6.4 a7.6 7.6 0 1 0 10.8 0"
        stroke={color}
        strokeWidth={2.4}
        strokeLinecap="round"
      />
    </Svg>
  );
}

function Sidebar() {
  const router = useRouter();
  const pathname = usePathname();
  const { available, user, signOut } = useAuth();
  const insets = useSafeAreaInsets();

  return (
    <View style={styles.panel}>
      <LinearGradient
        colors={['rgba(34, 29, 64, 0.96)', 'rgba(18, 16, 32, 0.93)', 'rgba(9, 8, 18, 0.97)']}
        locations={[0, 0.55, 1]}
        start={{ x: 0, y: 0 }}
        end={{ x: 0.9, y: 1 }}
        style={StyleSheet.absoluteFill}
      />
      {/* A single lit edge. It reads as thickness, which is what makes a
          translucent panel look like glass rather than like low opacity. */}
      <View style={styles.edge} pointerEvents="none" />

      <DrawerContentScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + space.md, paddingBottom: insets.bottom + space.md },
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.brand}>KOSMIQ</Text>

        <View style={styles.items}>
          {ITEMS.filter((item) => !item.accountOnly || user).map((item) => {
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
                <View style={[styles.marker, active && styles.markerActive]} />
                <Text style={[styles.glyph, active && styles.glyphActive]}>{item.glyph}</Text>
                <Text style={[styles.itemLabel, active && styles.itemLabelActive]}>
                  {item.label}
                </Text>
              </Pressable>
            );
          })}
        </View>

        {/* Pushes the account action to the bottom of the panel however short
            the list above it is. */}
        <View style={styles.spacer} />

        {available ? (
          user ? (
            <Pressable
              accessibilityRole="button"
              onPress={signOut}
              style={({ pressed }) => [
                styles.exit,
                styles.exitOut,
                pressed && styles.itemPressed,
              ]}
            >
              <PowerIcon color="#FFFFFF" />
              <Text style={[styles.exitLabel, styles.exitLabelFilled]}>Sign out</Text>
            </Pressable>
          ) : (
            <Pressable
              accessibilityRole="button"
              onPress={() => router.push('/sign-in')}
              style={({ pressed }) => [
                styles.exit,
                styles.exitIn,
                pressed && styles.itemPressed,
              ]}
            >
              <PowerIcon color="#FFFFFF" />
              <Text style={[styles.exitLabel, styles.exitLabelFilled]}>Sign in</Text>
            </Pressable>
          )
        ) : null}
      </DrawerContentScrollView>
    </View>
  );
}

export default function AppLayout() {
  return (
    <Drawer
      drawerContent={() => <Sidebar />}
      screenOptions={{
        headerShown: false,
        // 'front' is what makes transparency mean anything: the panel floats
        // over the screen rather than pushing it aside.
        drawerType: 'front',
        // 272 left 140dp of empty air: the longest label, SETTINGS, ends at
        // 132dp. Measured off a screenshot rather than guessed.
        drawerStyle: { backgroundColor: 'transparent', width: 200 },
        overlayColor: 'rgba(11, 10, 20, 0.55)',
        // Transparent: the root star field is the background now.
        sceneStyle: { backgroundColor: 'transparent' },
      }}
    />
  );
}

const styles = StyleSheet.create({
  panel: {
    flex: 1,
    // Matches the radius the drawer container itself applies for 'front', so
    // the gradient stops exactly where the panel is clipped.
    borderTopRightRadius: radius.md,
    borderBottomRightRadius: radius.md,
    overflow: 'hidden',
  },
  edge: {
    position: 'absolute',
    top: 0,
    bottom: 0,
    right: 0,
    width: StyleSheet.hairlineWidth * 2,
    backgroundColor: 'rgba(185, 174, 255, 0.22)',
  },
  scroll: { backgroundColor: 'transparent' },
  content: {
    flexGrow: 1,
    paddingHorizontal: space.sm,
  },
  brand: {
    ...type.label,
    color: colors.accentSoft,
    letterSpacing: 3,
    paddingHorizontal: space.md,
    marginBottom: space.xl,
  },

  items: { gap: 2 },
  item: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.md,
    height: 50,
    paddingRight: space.md,
    borderRadius: radius.md,
  },
  itemActive: { backgroundColor: 'rgba(139, 123, 247, 0.16)' },
  itemPressed: { opacity: 0.6 },
  // Sits in the row's left gutter so labels stay on one vertical line whether
  // or not the row is the active one.
  marker: {
    width: 3,
    height: 20,
    borderRadius: radius.pill,
    backgroundColor: 'transparent',
  },
  markerActive: { backgroundColor: colors.accent },
  glyph: { fontSize: 15, color: colors.textFaint, width: 18, textAlign: 'center' },
  glyphActive: { color: colors.accentSoft },
  itemLabel: {
    ...type.label,
    fontSize: 12,
    letterSpacing: 1.6,
    color: colors.textMuted,
  },
  itemLabelActive: { color: colors.text },

  spacer: { flex: 1, minHeight: space.xl },
  exit: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.sm,
    height: 46,
    paddingHorizontal: space.md,
    borderRadius: radius.md,
    borderWidth: StyleSheet.hairlineWidth,
    borderColor: 'transparent',
  },
  exitOut: { backgroundColor: colors.signOut },
  exitIn: { backgroundColor: colors.signIn },
  exitLabelFilled: { color: '#FFFFFF' },
  exitLabel: { ...type.label, fontSize: 12, letterSpacing: 1.6, color: colors.textMuted },
});

/**
 * The bar every screen inside the drawer wears.
 *
 * Its real job is the menu button. A drawer that can only be opened by swiping
 * from the bezel is a drawer most users never discover — the affordance has to
 * be on screen.
 */

import { useNavigation } from 'expo-router';
import type { DrawerNavigationProp } from 'expo-router/drawer';
import { ReactNode, useCallback } from 'react';
import { Pressable, StyleSheet, Text, View } from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { colors, space, type } from '../theme';

export function ScreenHeader({
  title,
  right,
  bordered = true,
}: {
  title?: string;
  right?: ReactNode;
  bordered?: boolean;
}) {
  // `openDrawer` lives on the drawer navigator, which is this screen's parent.
  const navigation = useNavigation<DrawerNavigationProp<Record<string, undefined>>>();
  const insets = useSafeAreaInsets();

  const open = useCallback(() => {
    navigation.openDrawer();
  }, [navigation]);

  return (
    <View
      style={[
        styles.header,
        bordered && styles.bordered,
        { paddingTop: insets.top + space.sm },
      ]}
    >
      <Pressable
        accessibilityRole="button"
        accessibilityLabel="Open menu"
        onPress={open}
        // A 44pt target: the icon itself is much smaller than a thumb.
        hitSlop={12}
        style={({ pressed }) => [styles.menu, pressed && styles.pressed]}
      >
        <View style={styles.bar} />
        <View style={[styles.bar, styles.barShort]} />
        <View style={styles.bar} />
      </Pressable>

      {title ? (
        <Text style={styles.title} numberOfLines={1}>
          {title}
        </Text>
      ) : (
        <View style={styles.spacer} />
      )}

      {right ?? null}
    </View>
  );
}

const styles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.md,
    paddingHorizontal: space.md,
    paddingBottom: space.sm,
  },
  bordered: {
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  menu: { width: 28, height: 28, justifyContent: 'center', gap: 5 },
  pressed: { opacity: 0.6 },
  bar: { height: 2, borderRadius: 1, backgroundColor: colors.textMuted },
  barShort: { width: '70%' },
  title: { ...type.heading, color: colors.text, flex: 1 },
  spacer: { flex: 1 },
});

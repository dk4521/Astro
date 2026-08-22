/**
 * The two-language toggle, for the header's right slot.
 *
 * Extracted because three screens had grown their own copy of it, and the
 * fourth and fifth — chart and today — had simply gone without: a control
 * duplicated by hand is a control that eventually goes missing somewhere, and
 * these two screens are where it was missed.
 */

import { Pressable, StyleSheet, Text, View } from 'react-native';

import { DISPLAY_LANGUAGES, type DisplayLanguage } from '../i18n';
import { colors, radius, space } from '../theme';

export function LanguagePicker({
  value,
  onChange,
}: {
  value: DisplayLanguage;
  onChange: (next: DisplayLanguage) => void;
}) {
  return (
    <View style={styles.group}>
      {DISPLAY_LANGUAGES.map((option) => {
        const active = option.value === value;
        return (
          <Pressable
            key={option.value}
            accessibilityRole="button"
            accessibilityState={{ selected: active }}
            onPress={() => onChange(option.value)}
            style={({ pressed }) => [
              styles.item,
              active && styles.itemActive,
              pressed && styles.pressed,
            ]}
          >
            <Text style={[styles.label, active && styles.labelActive]}>{option.label}</Text>
          </Pressable>
        );
      })}
    </View>
  );
}

const styles = StyleSheet.create({
  group: {
    flexDirection: 'row',
    backgroundColor: colors.glass,
    borderRadius: radius.pill,
    padding: 3,
    gap: 2,
  },
  item: {
    paddingHorizontal: space.sm + 2,
    paddingVertical: space.xs + 2,
    borderRadius: radius.pill,
  },
  itemActive: { backgroundColor: colors.accentDim },
  pressed: { opacity: 0.7 },
  label: { fontSize: 12, fontWeight: '600', color: colors.textFaint },
  labelActive: { color: colors.accentSoft },
});

/**
 * Small shared primitives. Kept in one file while the surface is this small —
 * splitting them out earns nothing until there are screens that disagree.
 */

import { ReactNode } from 'react';
import {
  ActivityIndicator,
  Pressable,
  StyleSheet,
  Text,
  View,
  ViewStyle,
} from 'react-native';

import { LinearGradient } from 'expo-linear-gradient';
import Svg, { Path } from 'react-native-svg';

import { colors, gradient, radius, space, type } from '../theme';

export function Label({ children }: { children: ReactNode }) {
  return <Text style={styles.label}>{children}</Text>;
}

export function Card({
  children,
  style,
}: {
  children: ReactNode;
  style?: ViewStyle;
}) {
  return <View style={[styles.card, style]}>{children}</View>;
}

export function Row({
  label,
  value,
  hint,
}: {
  label: string;
  value: string;
  hint?: string;
}) {
  return (
    <View style={styles.row}>
      <Text style={styles.rowLabel}>{label}</Text>
      <View style={styles.rowValueGroup}>
        <Text style={styles.rowValue}>{value}</Text>
        {hint ? <Text style={styles.rowHint}>{hint}</Text> : null}
      </View>
    </View>
  );
}

/**
 * A button.
 *
 * `tone` is what the button *is*, not what it looks like. Three actions carry a
 * colour of their own — leaving an account, entering one, and sending — and
 * everything else takes the brand gradient. Naming them by role rather than by
 * hex means the two sign-out buttons in the app cannot drift apart.
 */
export type Tone = 'brand' | 'signIn' | 'signOut' | 'send';

const TONE_FILL: Record<Exclude<Tone, 'brand'>, string> = {
  signIn: colors.signIn,
  signOut: colors.signOut,
  send: colors.send,
};

/** Text that sits on a filled button. Gold is light enough to need dark text. */
export function toneLabelColor(tone: Tone): string {
  return tone === 'send' ? colors.bg : tone === 'brand' ? colors.bg : '#FFFFFF';
}

export function Button({
  title,
  onPress,
  disabled,
  loading,
  variant = 'primary',
  tone = 'brand',
}: {
  title: string;
  onPress: () => void;
  disabled?: boolean;
  loading?: boolean;
  variant?: 'primary' | 'ghost';
  tone?: Tone;
}) {
  const inactive = disabled || loading;
  const filled = variant === 'primary';
  const solid = tone === 'brand' ? null : TONE_FILL[tone];

  const label = filled ? toneLabelColor(tone) : solid ?? colors.accentSoft;

  return (
    <Pressable
      accessibilityRole="button"
      accessibilityState={{ disabled: !!inactive, busy: !!loading }}
      onPress={onPress}
      disabled={inactive}
      style={({ pressed }) => [
        styles.button,
        // A solid tone paints itself; the gradient is a layer underneath.
        filled && solid ? { backgroundColor: solid } : null,
        !filled && { borderWidth: 1, borderColor: solid ?? colors.border },
        inactive && styles.buttonDisabled,
        pressed && !inactive && styles.buttonPressed,
      ]}
    >
      <LinearGradient
        colors={
          filled
            ? tone === 'brand'
              ? [...gradient.brand]
              : ['transparent', 'transparent']
            : [...gradient.brandSoft]
        }
        start={{ x: 0, y: 0 }}
        end={{ x: 1, y: 1 }}
        style={styles.buttonFill}
        pointerEvents="none"
      />
      {loading ? (
        <ActivityIndicator color={label} />
      ) : (
        <Text style={[styles.buttonText, { color: label }]}>{title}</Text>
      )}
    </Pressable>
  );
}

/**
 * Back.
 *
 * Drawn rather than typed: a chevron character like ‹ or ⟨ is missing from the
 * stock Android font on some devices and renders as an empty box, which is how
 * the power glyph in the sidebar failed.
 */
export function BackButton({ onPress }: { onPress: () => void }) {
  return (
    <Pressable
      accessibilityRole="button"
      accessibilityLabel="Go back"
      onPress={onPress}
      // The arrow is much smaller than a thumb; the target is not.
      hitSlop={12}
      style={({ pressed }) => [styles.back, pressed && styles.backPressed]}
    >
      <Svg width={20} height={20} viewBox="0 0 24 24" fill="none">
        <Path
          d="M15 4.5 L7.5 12 L15 19.5"
          stroke={colors.textMuted}
          strokeWidth={2.1}
          strokeLinecap="round"
          strokeLinejoin="round"
        />
      </Svg>
    </Pressable>
  );
}

export function Chip({ text, tone }: { text: string; tone?: 'retro' | 'combust' }) {
  const tint =
    tone === 'retro' ? colors.retro : tone === 'combust' ? colors.combust : colors.accentSoft;
  return (
    <View style={[styles.chip, { borderColor: tint }]}>
      <Text style={[styles.chipText, { color: tint }]}>{text}</Text>
    </View>
  );
}

export function ErrorNote({ message }: { message: string }) {
  return (
    <View style={styles.error}>
      <Text style={styles.errorText}>{message}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  label: {
    ...type.label,
    color: colors.textFaint,
    marginBottom: space.sm,
  },
  card: {
    backgroundColor: colors.glass,
    borderRadius: radius.md,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    padding: space.md,
  },
  row: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    paddingVertical: space.sm + 2,
    gap: space.md,
  },
  rowLabel: { ...type.body, color: colors.textMuted, flexShrink: 1 },
  rowValueGroup: { alignItems: 'flex-end', flexShrink: 1 },
  rowValue: { ...type.body, color: colors.text, fontWeight: '600', textAlign: 'right' },
  rowHint: { ...type.mono, color: colors.textFaint, marginTop: 2, textAlign: 'right' },
  button: {
    borderRadius: radius.pill,
    overflow: 'hidden',
    paddingVertical: space.md,
    paddingHorizontal: space.lg,
    alignItems: 'center',
    justifyContent: 'center',
    minHeight: 52,
  },
  // The gradient layer. Behind the label, in front of nothing — a fully
  // transparent pill would put its text straight onto the star field, where a
  // bright star can land inside a letter.
  buttonFill: { position: 'absolute', top: 0, left: 0, right: 0, bottom: 0 },
  buttonPressed: { opacity: 0.85 },
  buttonDisabled: { opacity: 0.4 },
  buttonText: { ...type.heading },
  back: { width: 28, height: 28, alignItems: 'center', justifyContent: 'center' },
  backPressed: { opacity: 0.6 },
  chip: {
    borderWidth: 1,
    borderRadius: radius.pill,
    paddingHorizontal: space.sm,
    paddingVertical: 2,
  },
  chipText: { fontSize: 10, fontWeight: '700', letterSpacing: 0.6 },
  error: {
    backgroundColor: 'rgba(74, 30, 46, 0.88)',
    borderColor: colors.combust,
    borderWidth: 1,
    borderRadius: radius.sm,
    padding: space.md,
  },
  errorText: { ...type.body, color: colors.combust },
});

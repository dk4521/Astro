/**
 * The sign-in and sign-up form.
 *
 * One component for both, because the difference between them is wording and a
 * single call — and two copies of a form drift until one of them stops
 * validating something the other does.
 */

import { useState } from 'react';
import {
  KeyboardAvoidingView,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { Button, ErrorNote, Label } from './ui';
import { colors, radius, space, type } from '../theme';

// Deliberately loose. Rejecting an address the server would have accepted is a
// worse failure than letting the server reject it.
const EMAIL = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
const MIN_PASSWORD = 6;

export function AuthForm({
  title,
  subtitle,
  action,
  onSubmit,
  footer,
  onSkip,
  notice,
}: {
  title: string;
  subtitle: string;
  action: string;
  onSubmit: (email: string, password: string) => Promise<string | null>;
  footer: { text: string; link: string; onPress: () => void };
  onSkip?: () => void;
  notice?: string | null;
}) {
  const insets = useSafeAreaInsets();

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [touched, setTouched] = useState(false);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const emailValid = EMAIL.test(email.trim());
  const passwordValid = password.length >= MIN_PASSWORD;
  const ready = emailValid && passwordValid;

  const submit = async () => {
    setTouched(true);
    if (!ready || busy) return;

    setBusy(true);
    setError(null);
    const message = await onSubmit(email, password);
    setBusy(false);
    if (message) setError(message);
  };

  return (
    <KeyboardAvoidingView style={styles.flex} behavior="padding">
      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + space.xxl, paddingBottom: insets.bottom + space.xl },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.kicker}>Kosmiq</Text>
        <Text style={styles.title}>{title}</Text>
        <Text style={styles.subtitle}>{subtitle}</Text>

        {notice ? (
          <View style={styles.notice}>
            <Text style={styles.noticeText}>{notice}</Text>
          </View>
        ) : null}

        <View style={styles.field}>
          <Label>Email</Label>
          <TextInput
            style={[styles.input, touched && !emailValid && styles.inputError]}
            value={email}
            onChangeText={setEmail}
            placeholder="you@example.com"
            placeholderTextColor={colors.textFaint}
            autoCapitalize="none"
            autoCorrect={false}
            keyboardType="email-address"
            textContentType="emailAddress"
            editable={!busy}
          />
          {touched && !emailValid ? (
            <Text style={styles.hintError}>Enter a valid email address.</Text>
          ) : null}
        </View>

        <View style={styles.field}>
          <Label>Password</Label>
          <TextInput
            style={[styles.input, touched && !passwordValid && styles.inputError]}
            value={password}
            onChangeText={setPassword}
            placeholder={`At least ${MIN_PASSWORD} characters`}
            placeholderTextColor={colors.textFaint}
            secureTextEntry
            autoCapitalize="none"
            autoCorrect={false}
            editable={!busy}
            onSubmitEditing={submit}
            returnKeyType="go"
          />
          {touched && !passwordValid ? (
            <Text style={styles.hintError}>
              Use at least {MIN_PASSWORD} characters.
            </Text>
          ) : null}
        </View>

        {error ? (
          <View style={styles.errorSlot}>
            <ErrorNote message={error} />
          </View>
        ) : null}

        <View style={styles.actions}>
          <Button title={action} onPress={submit} loading={busy} disabled={busy} />
        </View>

        <Pressable
          accessibilityRole="button"
          onPress={footer.onPress}
          disabled={busy}
          style={({ pressed }) => [styles.footer, pressed && styles.pressed]}
        >
          <Text style={styles.footerText}>
            {footer.text} <Text style={styles.footerLink}>{footer.link}</Text>
          </Text>
        </Pressable>

        {onSkip ? (
          <Pressable
            accessibilityRole="button"
            onPress={onSkip}
            disabled={busy}
            style={({ pressed }) => [styles.skip, pressed && styles.pressed]}
          >
            <Text style={styles.skipText}>Continue without an account</Text>
          </Pressable>
        ) : null}
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  content: { paddingHorizontal: space.lg },
  kicker: { ...type.label, color: colors.accent },
  title: { ...type.display, color: colors.text, marginTop: space.sm },
  subtitle: { ...type.body, color: colors.textMuted, lineHeight: 22, marginTop: space.sm, marginBottom: space.xl },
  notice: {
    backgroundColor: colors.accentDim,
    borderRadius: radius.sm,
    padding: space.md,
    marginBottom: space.lg,
  },
  noticeText: { ...type.body, color: colors.accentSoft, lineHeight: 21 },
  field: { marginBottom: space.lg },
  input: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    paddingVertical: space.md,
    color: colors.text,
    fontSize: 16,
  },
  inputError: { borderColor: colors.combust },
  hintError: { ...type.mono, color: colors.combust, marginTop: space.sm },
  errorSlot: { marginBottom: space.md },
  actions: { marginTop: space.sm },
  footer: { marginTop: space.lg, alignItems: 'center', paddingVertical: space.sm },
  footerText: { ...type.body, color: colors.textMuted },
  footerLink: { color: colors.accentSoft, fontWeight: '600' },
  skip: { marginTop: space.md, alignItems: 'center', paddingVertical: space.sm },
  skipText: { ...type.mono, color: colors.textFaint },
  pressed: { opacity: 0.7 },
});

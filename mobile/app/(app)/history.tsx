/**
 * Past conversations.
 *
 * Only reachable with an account, because only an account stores anything: on a
 * signed-out phone a conversation lives in React state and is gone the moment
 * the screen unmounts. The sidebar hides this route rather than showing it
 * empty, since an empty history and no history at all are different claims and
 * the second one is the true one.
 *
 * Read-only on purpose. Continuing an old thread would need the chat screen to
 * adopt a conversation id it did not open, and reading back is what the feature
 * was asked for.
 */

import { useFocusEffect } from 'expo-router';
import { useCallback, useState } from 'react';
import { ActivityIndicator, Pressable, ScrollView, StyleSheet, Text, View } from 'react-native';

import { useSync } from '../../src/sync/context';
import type { ConversationSummary, StoredTurn } from '../../src/sync/chat';
import { PERSONAS, Portrait } from '../../src/components/Avatar';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { RichText } from '../../src/components/RichText';
import { Label } from '../../src/components/ui';
import { colors, radius, space, type } from '../../src/theme';

/** "today", "yesterday", "13 Nov" — enough to place a conversation. */
function whenText(iso: string): string {
  const then = new Date(iso);
  const today = new Date();
  const days = Math.floor(
    (Date.UTC(today.getFullYear(), today.getMonth(), today.getDate()) -
      Date.UTC(then.getFullYear(), then.getMonth(), then.getDate())) /
      86_400_000,
  );
  if (days <= 0) return 'today';
  if (days === 1) return 'yesterday';
  if (days < 7) return `${days} days ago`;
  return then.toLocaleDateString(undefined, { day: 'numeric', month: 'short' });
}

export default function History() {
  const { enabled, listHistory, readConversation } = useSync();

  const [rows, setRows] = useState<ConversationSummary[] | null>(null);
  const [open, setOpen] = useState<ConversationSummary | null>(null);
  const [turns, setTurns] = useState<StoredTurn[] | null>(null);

  // On focus, not on mount. The drawer keeps its screens mounted, so a plain
  // effect runs once and then never again — the list showed a message count
  // taken before the answer it was counting had finished streaming, and no
  // amount of navigating back to it would correct the number.
  useFocusEffect(
    useCallback(() => {
      if (!enabled) {
        setRows([]);
        return;
      }
      let cancelled = false;
      listHistory().then((found) => {
        if (!cancelled) setRows(found);
      });
      return () => {
        cancelled = true;
      };
    }, [enabled, listHistory]),
  );

  const show = useCallback(
    (row: ConversationSummary) => {
      setOpen(row);
      setTurns(null);
      readConversation(row.id).then(setTurns);
    },
    [readConversation],
  );

  if (open) {
    const person = PERSONAS.find((p) => p.id === open.persona);
    return (
      <View style={styles.flex}>
        <ScreenHeader title={person?.name ?? 'Conversation'} onBack={() => setOpen(null)} />
        <ScrollView contentContainerStyle={styles.content}>
          {turns === null ? (
            <View style={styles.loading}>
              <ActivityIndicator color={colors.accent} />
            </View>
          ) : (
            turns.map((turn, i) =>
              turn.role === 'user' ? (
                <View key={i} style={styles.userRow}>
                  <View style={styles.userBubble}>
                    <Text style={styles.userText}>{turn.content}</Text>
                  </View>
                </View>
              ) : (
                <View key={i} style={styles.answer}>
                  <RichText text={turn.content} />
                </View>
              ),
            )
          )}
        </ScrollView>
      </View>
    );
  }

  return (
    <View style={styles.flex}>
      <ScreenHeader title="History" />
      <ScrollView contentContainerStyle={styles.content}>
        {rows === null ? (
          <View style={styles.loading}>
            <ActivityIndicator color={colors.accent} />
          </View>
        ) : rows.length === 0 ? (
          <Text style={styles.empty}>
            {enabled
              ? 'Nothing here yet. Conversations are kept once you have had one.'
              : 'Sign in to keep your conversations.'}
          </Text>
        ) : (
          <>
            <Label>{`${rows.length} conversation${rows.length === 1 ? '' : 's'}`}</Label>
            {rows.map((row) => {
              const person = PERSONAS.find((p) => p.id === row.persona);
              return (
                <Pressable
                  key={row.id}
                  accessibilityRole="button"
                  onPress={() => show(row)}
                  style={({ pressed }) => [styles.row, pressed && styles.pressed]}
                >
                  {person ? (
                    <Portrait person={person} size={44} />
                  ) : (
                    <View style={styles.noFace} />
                  )}
                  <View style={styles.rowText}>
                    <Text style={styles.rowName}>{person?.name ?? 'Conversation'}</Text>
                    <Text style={styles.rowMeta}>
                      {whenText(row.createdAt)} · {row.turns} message
                      {row.turns === 1 ? '' : 's'}
                    </Text>
                  </View>
                </Pressable>
              );
            })}
          </>
        )}
      </ScrollView>
    </View>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg, paddingBottom: space.xxl },
  loading: { paddingVertical: space.xxl, alignItems: 'center' },
  empty: { ...type.body, color: colors.textMuted, lineHeight: 22 },
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: space.md,
    padding: space.md,
    marginTop: space.sm,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    borderRadius: radius.md,
  },
  noFace: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: colors.glassRaised,
  },
  rowText: { flex: 1 },
  rowName: { ...type.heading, color: colors.text },
  rowMeta: { ...type.mono, color: colors.textFaint, marginTop: 2 },
  pressed: { opacity: 0.7 },
  userRow: { alignItems: 'flex-end', marginTop: space.lg },
  userBubble: {
    maxWidth: '88%',
    backgroundColor: 'rgba(58, 50, 110, 0.88)',
    borderWidth: 1,
    borderColor: 'rgba(185, 174, 255, 0.30)',
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingVertical: space.sm + 2,
  },
  userText: { ...type.body, color: colors.text, lineHeight: 21 },
  answer: {
    marginTop: space.md,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    borderRadius: radius.md,
    padding: space.md,
  },
});

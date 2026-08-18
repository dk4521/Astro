/**
 * The reading — the chart explained, and a conversation about it.
 *
 * This screen is where the product's central claim becomes visible or fails to:
 * every number in the text was computed before the model saw it, and the
 * backend checks the generated text back against the chart afterwards. That
 * check is shown, not hidden. A reading that contradicts the chart says so on
 * screen, because a guarantee the user cannot see is a marketing line.
 *
 * The opening reading and the conversation are kept apart on purpose. The
 * backend folds the chart brief into the first history turn whatever its role,
 * so an assistant turn in position zero would be replayed as if the user had
 * written it — see `streamChat` in `src/api/client.ts`.
 *
 * With an account, the conversation is stored and read back (`src/sync/chat.ts`)
 * — it is the one thing here that cannot be recomputed. The opening reading is
 * not stored: it is generated fresh from the chart in whichever language is
 * selected, so a saved copy would only be a stale duplicate. Signed out, the
 * conversation lives as long as the screen does, exactly as it always has.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useRef, useState } from 'react';
import {
  ActivityIndicator,
  KeyboardAvoidingView,
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';
import { useSafeAreaInsets } from 'react-native-safe-area-context';

import { streamChat } from '../../src/api/client';
import { loadInterpretation } from '../../src/api/reading';
import { loadBirthDetails } from '../../src/api/storage';
import { useSync } from '../../src/sync/context';
import type { BirthDetails, ChatTurn, Language } from '../../src/api/types';
import { RichText } from '../../src/components/RichText';
import { ScreenHeader } from '../../src/components/ScreenHeader';
import { Button, ErrorNote, Label } from '../../src/components/ui';
import { colors, radius, space, type } from '../../src/theme';

/**
 * The most turns `/v1/chat` will accept — `ChatRequest.history` in
 * `backend/app/schemas.py`. A restored conversation can be longer than the
 * model is allowed to see, so what goes up is the tail of it.
 */
const HISTORY_TURNS = 40;

const LANGUAGES: { value: Language; label: string }[] = [
  { value: 'hinglish', label: 'Hinglish' },
  { value: 'hi', label: 'हिंदी' },
  { value: 'en', label: 'English' },
];

/** Openers, in the language they will be answered in. */
const SUGGESTIONS: Record<Language, string[]> = {
  hinglish: [
    'Abhi ka dasha period kya keh raha hai?',
    'Mera Moon aur janma nakshatra kaisa hai?',
    'Kaam aur career ke baare mein batao',
  ],
  hi: [
    'अभी की दशा क्या कह रही है?',
    'मेरा चंद्रमा और जन्म नक्षत्र कैसा है?',
    'काम और करियर के बारे में बताइए',
  ],
  en: [
    'What is my current dasha about?',
    'Tell me about my Moon and janma nakshatra',
    'What does this period ask of me?',
  ],
};

type Message = {
  id: number;
  role: 'user' | 'assistant';
  text: string;
  streaming?: boolean;
  grounded?: boolean;
  contradictions?: string[];
};

/**
 * What the grounding check found, stated plainly.
 *
 * The quiet case is deliberately quiet — a tick and a line of small text, not a
 * badge — because "the numbers are right" is the baseline here rather than an
 * achievement. The loud case is loud.
 */
function GroundingNote({
  grounded,
  contradictions,
}: {
  grounded?: boolean;
  contradictions?: string[];
}) {
  if (grounded === undefined) return null;

  if (grounded) {
    return <Text style={styles.groundedOk}>✓ Checked against your computed chart</Text>;
  }

  return (
    <View style={styles.groundedBad}>
      <Text style={styles.groundedBadTitle}>
        This disagrees with your chart
      </Text>
      {(contradictions ?? []).map((line) => (
        <Text key={line} style={styles.groundedBadLine}>
          {line}
        </Text>
      ))}
      <Text style={styles.groundedBadFoot}>
        The chart screen holds the computed values. Those are the correct ones.
      </Text>
    </View>
  );
}

export default function ReadingScreen() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { enabled: syncing, chartId, loadChatHistory, recordTurn } = useSync();

  const [details, setDetails] = useState<BirthDetails | null>(null);
  const [language, setLanguage] = useState<Language>('hinglish');

  const [opening, setOpening] = useState<Message | null>(null);
  const [openingLoading, setOpeningLoading] = useState(true);
  const [slow, setSlow] = useState(false);

  const [messages, setMessages] = useState<Message[]>([]);
  const [question, setQuestion] = useState('');
  const [sending, setSending] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const scroller = useRef<ScrollView>(null);
  const abort = useRef<AbortController | null>(null);
  const nextId = useRef(1);
  // Switching language starts a second reading while the first is still in
  // flight, and `/v1/interpret` has no cancellation. Without this the slower
  // response wins whenever it happens to land last, so the screen can end up
  // showing Hinglish under a selected हिंदी pill. Same guard the place search
  // in `onboarding.tsx` uses.
  const openingRequest = useRef(0);
  // Which chart's history has been read back. The sync context hands out a new
  // `loadChatHistory` whenever its status changes, and re-running the restore
  // would wipe whatever has been asked since.
  const restoredFor = useRef<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      const saved = await loadBirthDetails();
      if (cancelled) return;
      if (!saved) {
        router.replace('/onboarding');
        return;
      }
      setDetails(saved);
    })();
    return () => {
      cancelled = true;
    };
  }, [router]);

  // Past turns, once. They arrive after the first paint, which is right: the
  // reading is what this screen is for, and the transcript below it can fill in.
  useEffect(() => {
    if (!syncing || !chartId || restoredFor.current === chartId) return;
    restoredFor.current = chartId;

    let cancelled = false;
    loadChatHistory().then((turns) => {
      if (cancelled || turns.length === 0) return;
      setMessages(
        turns.map((turn) => ({
          id: nextId.current++,
          role: turn.role,
          text: turn.content,
          grounded: turn.grounded,
          contradictions: turn.contradictions,
        })),
      );
    });

    return () => {
      cancelled = true;
    };
  }, [syncing, chartId, loadChatHistory]);

  const loadOpening = useCallback(
    async (birth: BirthDetails, lang: Language) => {
      const id = ++openingRequest.current;
      setOpeningLoading(true);
      setError(null);
      // A reading was measured between 2s and 80s on the free tier. A spinner
      // that says nothing for a minute reads as a hang, so say what is going on.
      // Only a first reading waits at all: the same chart, language and day come
      // back from the device (`src/api/reading.ts`) before this timer starts.
      const slowTimer = setTimeout(() => setSlow(true), 10_000);

      try {
        const result = await loadInterpretation(birth, lang);
        if (id !== openingRequest.current) return;
        setOpening({
          id: 0,
          role: 'assistant',
          text: result.text,
          grounded: result.grounded,
          contradictions: result.contradictions,
        });
      } catch (err) {
        if (id !== openingRequest.current) return;
        setOpening(null);
        setError(err instanceof Error ? err.message : 'Could not reach the interpreter');
      } finally {
        clearTimeout(slowTimer);
        if (id === openingRequest.current) {
          setSlow(false);
          setOpeningLoading(false);
        }
      }
    },
    [],
  );

  useEffect(() => {
    if (!details) return;
    loadOpening(details, language);
  }, [details, language, loadOpening]);

  const stop = useCallback(() => {
    abort.current?.abort();
    abort.current = null;
  }, []);

  // Leaving mid-answer should not leave a request running.
  useEffect(() => () => abort.current?.abort(), []);

  const changeLanguage = useCallback(
    (next: Language) => {
      if (next === language) return;
      stop();
      setLanguage(next);
    },
    [language, stop],
  );

  const ask = useCallback(
    async (text: string) => {
      const trimmed = text.trim();
      if (!trimmed || !details || sending) return;

      setQuestion('');
      setError(null);
      setSending(true);

      // The history is the conversation only — never the opening reading.
      const history: ChatTurn[] = messages
        .filter((message) => message.text.trim().length > 0)
        .map((message) => ({ role: message.role, content: message.text }))
        .slice(-HISTORY_TURNS);

      const askedId = nextId.current++;
      const answerId = nextId.current++;

      setMessages((current) => [
        ...current,
        { id: askedId, role: 'user', text: trimmed },
        { id: answerId, role: 'assistant', text: '', streaming: true },
      ]);

      // Recorded before the answer exists, because it was asked whether or not
      // one arrives. Inserts are queued in call order by the sync context, so
      // this lands ahead of the reply it belongs to.
      void recordTurn({ role: 'user', content: trimmed }, language);

      const controller = new AbortController();
      abort.current = controller;

      const update = (change: Partial<Message>) =>
        setMessages((current) =>
          current.map((message) =>
            message.id === answerId ? { ...message, ...change } : message,
          ),
        );

      // Accumulated here as well as in state: the verdict and the final text
      // are needed together when the stream ends, and a `setMessages` updater
      // cannot be read back synchronously.
      let answer = '';
      // Left uninitialised on purpose: `= null` would narrow it to `null` for
      // the read below, since TypeScript does not track the assignment made
      // inside `onVerdict`.
      let verdict: { grounded: boolean; contradictions: string[] } | undefined;

      try {
        await streamChat(
          { birth: details, question: trimmed, language, history },
          {
            onToken: (chunk) => {
              answer += chunk;
              setMessages((current) =>
                current.map((message) =>
                  message.id === answerId
                    ? { ...message, text: message.text + chunk }
                    : message,
                ),
              );
            },
            onVerdict: (next) => {
              verdict = next;
              update({ grounded: next.grounded, contradictions: next.contradictions });
            },
          },
          controller.signal,
        );
      } catch (err) {
        setError(err instanceof Error ? err.message : 'The answer was interrupted');
      } finally {
        update({ streaming: false });
        // An answer that produced nothing at all is noise in the transcript.
        setMessages((current) =>
          current.filter(
            (message) => message.id !== answerId || message.text.trim().length > 0,
          ),
        );

        // A partial answer is still stored, with whatever verdict it got. An
        // answer that was cut short is part of what happened, and dropping it
        // would leave the question above it looking unanswered.
        if (answer.trim().length > 0) {
          void recordTurn(
            {
              role: 'assistant',
              content: answer,
              grounded: verdict?.grounded,
              contradictions: verdict?.contradictions,
            },
            language,
          );
        }

        abort.current = null;
        setSending(false);
      }
    },
    [details, language, messages, sending, recordTurn],
  );

  const retry = useCallback(() => {
    if (details) loadOpening(details, language);
  }, [details, language, loadOpening]);

  return (
    // `padding` on Android too, which the usual advice says is unnecessary
    // because the window resizes itself. Under Android's edge-to-edge — not
    // optional since SDK 54 — it does not resize, and leaving `behavior`
    // undefined put the composer and the send button completely underneath the
    // keyboard. Caught on a device; no emulator or typecheck would have shown it.
    <KeyboardAvoidingView
      style={styles.flex}
      behavior="padding"
      keyboardVerticalOffset={0}
    >
      <ScreenHeader
        right={
          <View style={styles.langGroup}>
          {LANGUAGES.map((option) => {
            const active = option.value === language;
            return (
              <Pressable
                key={option.value}
                accessibilityRole="button"
                accessibilityState={{ selected: active }}
                onPress={() => changeLanguage(option.value)}
                style={({ pressed }) => [
                  styles.lang,
                  active && styles.langActive,
                  pressed && styles.pressed,
                ]}
              >
                <Text style={[styles.langText, active && styles.langTextActive]}>
                  {option.label}
                </Text>
              </Pressable>
            );
          })}
          </View>
        }
      />

      <ScrollView
        ref={scroller}
        style={styles.flex}
        contentContainerStyle={[styles.content, { paddingBottom: space.xl }]}
        keyboardShouldPersistTaps="handled"
        onContentSizeChange={() => {
          if (sending) scroller.current?.scrollToEnd({ animated: true });
        }}
      >
        <Text style={styles.kicker}>Your reading</Text>

        {openingLoading ? (
          <View style={styles.waiting}>
            <ActivityIndicator color={colors.accent} />
            <Text style={styles.waitingText}>Reading your chart…</Text>
            {slow ? (
              <Text style={styles.waitingSlow}>
                Still working. This can take up to a minute.
              </Text>
            ) : null}
          </View>
        ) : null}

        {error && !opening ? (
          <View style={styles.errorSlot}>
            <ErrorNote message={error} />
            <View style={styles.retry}>
              <Button title="Try again" onPress={retry} variant="ghost" />
            </View>
          </View>
        ) : null}

        {opening ? (
          <View style={styles.openingBlock}>
            <RichText text={opening.text} />
            <GroundingNote
              grounded={opening.grounded}
              contradictions={opening.contradictions}
            />
          </View>
        ) : null}

        {opening && messages.length === 0 ? (
          <View style={styles.suggestions}>
            <Label>Ask about it</Label>
            {SUGGESTIONS[language].map((suggestion) => (
              <Pressable
                key={suggestion}
                accessibilityRole="button"
                onPress={() => ask(suggestion)}
                style={({ pressed }) => [styles.suggestion, pressed && styles.pressed]}
              >
                <Text style={styles.suggestionText}>{suggestion}</Text>
              </Pressable>
            ))}
          </View>
        ) : null}

        {messages.map((message) =>
          message.role === 'user' ? (
            <View key={message.id} style={styles.userRow}>
              <View style={styles.userBubble}>
                <Text style={styles.userText}>{message.text}</Text>
              </View>
            </View>
          ) : (
            <View key={message.id} style={styles.answerBlock}>
              {message.text.length > 0 ? (
                <RichText text={message.text} />
              ) : (
                <View style={styles.thinking}>
                  <ActivityIndicator color={colors.textFaint} size="small" />
                  <Text style={styles.thinkingText}>Thinking…</Text>
                </View>
              )}
              {message.streaming ? null : (
                <GroundingNote
                  grounded={message.grounded}
                  contradictions={message.contradictions}
                />
              )}
            </View>
          ),
        )}

        {error && opening ? (
          <View style={styles.errorSlot}>
            <ErrorNote message={error} />
          </View>
        ) : null}
      </ScrollView>

      <View style={[styles.composer, { paddingBottom: insets.bottom + space.sm }]}>
        <TextInput
          style={styles.input}
          value={question}
          onChangeText={setQuestion}
          placeholder="Ask about your chart"
          placeholderTextColor={colors.textFaint}
          multiline
          maxLength={2000}
          editable={!sending}
          onSubmitEditing={() => ask(question)}
          returnKeyType="send"
        />
        <Pressable
          accessibilityRole="button"
          accessibilityLabel={sending ? 'Stop' : 'Send'}
          onPress={() => (sending ? stop() : ask(question))}
          disabled={!sending && question.trim().length === 0}
          style={({ pressed }) => [
            styles.send,
            !sending && question.trim().length === 0 && styles.sendDisabled,
            pressed && styles.pressed,
          ]}
        >
          <Text style={styles.sendText}>{sending ? '■' : '↑'}</Text>
        </Pressable>
      </View>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: colors.bg },
  pressed: { opacity: 0.7 },
  langGroup: {
    flexDirection: 'row',
    backgroundColor: colors.surface,
    borderRadius: radius.pill,
    padding: 3,
    gap: 2,
  },
  lang: {
    paddingHorizontal: space.sm + 2,
    paddingVertical: space.xs + 2,
    borderRadius: radius.pill,
  },
  langActive: { backgroundColor: colors.accentDim },
  langText: { fontSize: 12, fontWeight: '600', color: colors.textFaint },
  langTextActive: { color: colors.accentSoft },
  content: { paddingHorizontal: space.lg, paddingTop: space.lg },
  kicker: { ...type.label, color: colors.accent },
  waiting: { alignItems: 'center', gap: space.sm, paddingVertical: space.xl },
  waitingText: { ...type.body, color: colors.textMuted },
  waitingSlow: {
    ...type.mono,
    color: colors.textFaint,
    textAlign: 'center',
    paddingHorizontal: space.lg,
  },
  openingBlock: { gap: space.md },
  suggestions: { marginTop: space.xl, gap: space.sm },
  suggestion: {
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    paddingVertical: space.md,
  },
  suggestionText: { ...type.body, color: colors.textMuted },
  userRow: { alignItems: 'flex-end', marginTop: space.xl },
  userBubble: {
    maxWidth: '88%',
    backgroundColor: colors.accentDim,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingVertical: space.sm + 2,
  },
  userText: { ...type.body, color: colors.text, lineHeight: 21 },
  answerBlock: { marginTop: space.lg, gap: space.md },
  thinking: { flexDirection: 'row', alignItems: 'center', gap: space.sm },
  thinkingText: { ...type.body, color: colors.textFaint },
  groundedOk: { ...type.mono, color: colors.textFaint },
  groundedBad: {
    backgroundColor: 'rgba(228, 114, 143, 0.12)',
    borderColor: colors.combust,
    borderWidth: 1,
    borderRadius: radius.sm,
    padding: space.md,
    gap: space.xs,
  },
  groundedBadTitle: { ...type.heading, color: colors.combust },
  groundedBadLine: { ...type.mono, color: colors.combust, lineHeight: 18 },
  groundedBadFoot: { ...type.mono, color: colors.textMuted, marginTop: space.xs },
  errorSlot: { marginTop: space.lg },
  retry: { marginTop: space.md },
  composer: {
    flexDirection: 'row',
    alignItems: 'flex-end',
    gap: space.sm,
    paddingHorizontal: space.md,
    paddingTop: space.sm,
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
    backgroundColor: colors.bg,
  },
  input: {
    flex: 1,
    maxHeight: 120,
    backgroundColor: colors.surface,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingTop: space.sm + 2,
    paddingBottom: space.sm + 2,
    color: colors.text,
    fontSize: 16,
  },
  send: {
    width: 44,
    height: 44,
    borderRadius: radius.pill,
    backgroundColor: colors.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  sendDisabled: { opacity: 0.35 },
  sendText: { fontSize: 18, fontWeight: '700', color: colors.bg },
});

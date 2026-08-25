/**
 * Tarot.
 *
 * The one screen in this app where something is genuinely random — and it is
 * handled the way everything else here is handled: by making it reproducible.
 * The shuffle is a seed, the seed is printed under the cards, and the same seed
 * deals the same hand on any phone, forever. Nothing is stored on the server.
 *
 * **Two layers, and only one of them costs anything.** Turning the cards over
 * and reading what each one means is free, works signed out, and calls no
 * model: those lines were written by a person and are the same for everyone.
 * Having the three read together as one thing is the paid layer, and it is a
 * deliberate tap with the price stated next to it — never something that
 * happens because a screen loaded.
 *
 * **The spread is not past / present / future.** A timeline is a forecast, and
 * this product does not forecast. Situation, obstacle, advice asks the same
 * three questions and lands the last card on something the reader can actually
 * do, which is the same choice the dasha meanings make.
 */

import { useRouter } from 'expo-router';
import { useCallback, useEffect, useMemo, useState } from 'react';
import {
  Pressable,
  ScrollView,
  StyleSheet,
  Text,
  TextInput,
  View,
} from 'react-native';

import {
  QUIET_ABOVE,
  isSubscribed,
  loadAllowance,
  looksLikeCrisis,
  type Allowance,
} from '../../../src/api/allowance';
import { ApiError } from '../../../src/api/client';
import { loadDisplayLanguage, saveDisplayLanguage } from '../../../src/api/storage';
import {
  cachedTarotReading,
  loadLastDraw,
  loadTarotReading,
  newDraw,
  readingRequestId,
  rememberRevealed,
} from '../../../src/api/tarot';
import type { TarotDraw, TarotReading } from '../../../src/api/types';
import { useAuth } from '../../../src/auth/context';
import { LanguagePicker } from '../../../src/components/LanguagePicker';
import { RichText } from '../../../src/components/RichText';
import { ScreenHeader } from '../../../src/components/ScreenHeader';
import { TarotCardFace, cardColour } from '../../../src/components/TarotCard';
import { Button, Card, ErrorNote, Label } from '../../../src/components/ui';
import { strings, type DisplayLanguage } from '../../../src/i18n';
import { colors, radius, space, type } from '../../../src/theme';

export default function Tarot() {
  const router = useRouter();
  const { available: accountsAvailable, user } = useAuth();

  const [language, setLanguage] = useState<DisplayLanguage>('en');
  const [drawn, setDrawn] = useState<TarotDraw | null>(null);
  const [revealed, setRevealed] = useState<string[]>([]);
  const [question, setQuestion] = useState('');
  const [dealing, setDealing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const [reading, setReading] = useState<TarotReading | null>(null);
  const [readingLoading, setReadingLoading] = useState(false);
  const [readingError, setReadingError] = useState<string | null>(null);
  const [blocked, setBlocked] = useState<{ crisis: boolean } | null>(null);

  const [allowance, setAllowance] = useState<Allowance | null>(null);

  const t = strings(language);

  useEffect(() => {
    loadDisplayLanguage().then(setLanguage);
  }, []);

  useEffect(() => {
    void (async () => {
      setAllowance(await loadAllowance(user?.id ?? null));
    })();
  }, [user]);

  // The spread the reader left behind, with the cards they had already turned.
  useEffect(() => {
    let cancelled = false;
    void (async () => {
      const stored = await loadLastDraw();
      if (cancelled || !stored) return;
      setDrawn(stored.draw);
      setRevealed(stored.revealed);
    })();
    return () => {
      cancelled = true;
    };
  }, []);

  /**
   * A reading belongs to the language it was written in.
   *
   * Switching the pill shows whatever was already paid for in the new language
   * and otherwise shows the button again — it never re-buys silently. The old
   * reading stays on the device, so switching back is instant and free.
   */
  useEffect(() => {
    let cancelled = false;
    if (!drawn) return;

    void (async () => {
      const stored = await cachedTarotReading(drawn.seed, language);
      if (cancelled) return;
      setReading(stored?.reading ?? null);
      if (stored) setQuestion(stored.question);
    })();

    return () => {
      cancelled = true;
    };
  }, [drawn, language]);

  const chooseLanguage = useCallback((next: DisplayLanguage) => {
    setLanguage(next);
    void saveDisplayLanguage(next);
  }, []);

  const deal = useCallback(async () => {
    if (dealing) return;
    setDealing(true);
    setError(null);
    setReading(null);
    setReadingError(null);
    setBlocked(null);

    try {
      const next = await newDraw();
      setDrawn(next);
      setRevealed([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : t.unreachable);
    } finally {
      setDealing(false);
    }
  }, [dealing, t]);

  const turn = useCallback(
    (positionId: string) => {
      if (!drawn || revealed.includes(positionId)) return;
      const next = [...revealed, positionId];
      setRevealed(next);
      void rememberRevealed(drawn, next);
    },
    [drawn, revealed],
  );

  const allTurned = drawn !== null && revealed.length === drawn.cards.length;

  const read = useCallback(async () => {
    if (!drawn || readingLoading) return;

    // Checked at the moment of asking rather than in the button's disabled
    // state: the balance is read from the account and can be a message stale if
    // two devices are talking at once.
    if (allowance && allowance.balance <= 0) {
      setBlocked({ crisis: looksLikeCrisis(question) });
      return;
    }

    setReadingLoading(true);
    setReadingError(null);

    try {
      const requestId = readingRequestId(drawn.seed, question, language);
      setReading(await loadTarotReading(drawn.seed, question, language, requestId));
    } catch (err) {
      if (err instanceof ApiError && err.status === 402) {
        setBlocked({ crisis: looksLikeCrisis(question) });
      } else if (err instanceof ApiError && err.status === 401) {
        setReadingError(t.signInToAsk);
      } else {
        setReadingError(err instanceof Error ? err.message : t.tarotReadingFailed);
      }
    } finally {
      setReadingLoading(false);
      setAllowance(await loadAllowance(user?.id ?? null));
    }
  }, [drawn, question, language, readingLoading, allowance, user, t]);

  const spreadName = useMemo(
    () => (drawn ? (language === 'hi' ? drawn.spread_hi : drawn.spread) : ''),
    [drawn, language],
  );

  return (
    <View style={styles.flex}>
      <ScreenHeader
        title={t.tarot}
        right={<LanguagePicker value={language} onChange={chooseLanguage} />}
      />

      <ScrollView
        contentContainerStyle={styles.content}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.kicker}>{drawn ? spreadName : t.tarotIntro}</Text>

        {error ? <ErrorNote message={error} /> : null}

        {drawn === null ? (
          <Card style={styles.ask}>
            <QuestionField value={question} onChange={setQuestion} language={language} />
            <View style={styles.action}>
              <Button title={t.tarotDraw} onPress={deal} loading={dealing} />
            </View>
          </Card>
        ) : (
          <>
            <View style={styles.spread}>
              {drawn.cards.map((item, index) => {
                const open = revealed.includes(item.position.id);
                const label = language === 'hi' ? item.position.name_hi : item.position.name;
                return (
                  <View key={item.position.id} style={styles.column}>
                    <TarotCardFace
                      card={item.card}
                      reversed={item.reversed}
                      revealed={open}
                      language={language}
                      index={index}
                      onPress={open ? undefined : () => turn(item.position.id)}
                      accessibilityLabel={label}
                    />
                    <Text style={styles.position}>{label}</Text>
                  </View>
                );
              })}
            </View>

            {allTurned ? null : <Text style={styles.hint}>{t.tarotTurn}</Text>}

            {drawn.cards
              .filter((item) => revealed.includes(item.position.id))
              .map((item) => {
                const tint = cardColour(item.card);
                return (
                  <Card key={item.position.id} style={styles.detail}>
                    <View style={styles.detailHead}>
                      <Text style={styles.detailPosition}>
                        {language === 'hi' ? item.position.name_hi : item.position.name}
                      </Text>
                      {/* Orientation as a fact, in the card's own colour —
                          never in a colour that would rank it. */}
                      <View style={[styles.orient, { borderColor: tint }]}>
                        <Text style={[styles.orientText, { color: tint }]}>
                          {item.reversed ? t.tarotReversed : t.tarotUpright}
                        </Text>
                      </View>
                    </View>

                    <Text style={[styles.cardName, { color: tint }]}>
                      {language === 'hi' ? item.card.name_hi : item.card.name}
                    </Text>
                    <Text style={styles.keywords}>
                      {language === 'hi' ? item.card.keywords_hi : item.card.keywords}
                    </Text>
                    <Text style={styles.meaning}>
                      {language === 'hi' ? item.meaning_hi : item.meaning}
                    </Text>
                  </Card>
                );
              })}

            {allTurned ? (
              <ReadingBlock
                accountsAvailable={accountsAvailable}
                signedIn={Boolean(user)}
                allowance={allowance}
                blocked={blocked}
                reading={reading}
                loading={readingLoading}
                error={readingError}
                language={language}
                question={question}
                onQuestionChange={setQuestion}
                onRead={read}
                onSignIn={() => router.push('/sign-in')}
                onPlans={() => router.push('/plans')}
              />
            ) : null}

            {/* The honest footnote, and the reason this screen can call itself
                reproducible at all. One line, not three: the two paragraphs
                that used to follow it said the same thing as each other and
                were read once and then scrolled past forever. The seed earns
                its place because it is the only part anyone can act on — it
                deals this hand again. */}
            <Text style={styles.seed}>{t.tarotShuffle(drawn.seed)}</Text>

            <View style={styles.action}>
              <Button
                title={t.tarotDrawAgain}
                onPress={deal}
                loading={dealing}
                variant="ghost"
              />
            </View>
          </>
        )}

        <Pressable
          accessibilityRole="button"
          onPress={() => router.push('/tarot/deck')}
          style={({ pressed }) => [styles.deckLink, pressed && styles.pressed]}
        >
          <Text style={styles.deckLinkText}>{t.tarotDeckLink}</Text>
        </Pressable>
      </ScrollView>
    </View>
  );
}

/**
 * The question, wherever it is being asked from.
 *
 * It appears twice: before the shuffle, which is the traditional order and the
 * one most people expect, and again beside the button that pays for a reading —
 * because someone who dealt three cards on a whim and then found something to
 * ask should not have to shuffle again to ask it.
 */
function QuestionField({
  value,
  onChange,
  language,
}: {
  value: string;
  onChange: (next: string) => void;
  language: DisplayLanguage;
}) {
  const t = strings(language);
  return (
    <>
      <Label>{t.tarotQuestionLabel}</Label>
      <TextInput
        style={styles.input}
        value={value}
        onChangeText={onChange}
        placeholder={t.tarotQuestionPlaceholder}
        placeholderTextColor={colors.textFaint}
        multiline
        maxLength={2000}
      />
    </>
  );
}

/**
 * The paid half, and everything that can stand between someone and it.
 *
 * Split out because it is four mutually exclusive states — no account, out of
 * credits, a reading, or the offer of one — and reading four of those inline
 * inside the spread is how a screen becomes unmaintainable.
 */
function ReadingBlock({
  accountsAvailable,
  signedIn,
  allowance,
  blocked,
  reading,
  loading,
  error,
  language,
  question,
  onQuestionChange,
  onRead,
  onSignIn,
  onPlans,
}: {
  accountsAvailable: boolean;
  signedIn: boolean;
  allowance: Allowance | null;
  blocked: { crisis: boolean } | null;
  reading: TarotReading | null;
  loading: boolean;
  error: string | null;
  language: DisplayLanguage;
  question: string;
  onQuestionChange: (next: string) => void;
  onRead: () => void;
  onSignIn: () => void;
  onPlans: () => void;
}) {
  const t = strings(language);

  if (accountsAvailable && !signedIn) {
    return (
      <Card style={styles.gate}>
        <Text style={styles.gateTitle}>{t.tarotSignIn}</Text>
        <Text style={styles.gateBody}>{t.tarotSignInWhy}</Text>
        <View style={styles.action}>
          <Button title={t.signInAction} onPress={onSignIn} tone="signIn" />
        </View>
      </Card>
    );
  }

  if (blocked) {
    return (
      <Card style={styles.gate}>
        {blocked.crisis ? (
          <>
            <Text style={styles.gateTitle}>{t.crisisHeading}</Text>
            <Text style={styles.helplines}>{t.crisisHelplines}</Text>
            {isSubscribed(allowance) ? null : (
              <Text style={styles.gateBody}>{t.comesBackTomorrow}</Text>
            )}
          </>
        ) : (
          <>
            <Text style={styles.gateTitle}>{t.outOfMessages}</Text>
            <Text style={styles.gateBody}>
              {isSubscribed(allowance) ? t.outOfMessagesPaid : t.outOfMessagesFree}
            </Text>
            <View style={styles.action}>
              <Button title={t.upgrade} onPress={onPlans} />
            </View>
            {/* Quiet and always here: the crisis check is keyword matching and
                will miss phrasings it was never taught. */}
            <Text style={styles.helplinesQuiet}>{t.crisisHelplines}</Text>
          </>
        )}
      </Card>
    );
  }

  if (reading) {
    return (
      <Card style={styles.readingCard}>
        <RichText text={reading.text} />
        {/* Shown rather than hidden. A reading that named a card the shuffle
            never dealt is the product's one visible failure, and covering it up
            would be worse than printing it. */}
        {reading.grounded ? null : (
          <Text style={styles.flagged}>{t.tarotUngrounded}</Text>
        )}
      </Card>
    );
  }

  return (
    <Card style={styles.offer}>
      {error ? <ErrorNote message={error} /> : null}
      <QuestionField value={question} onChange={onQuestionChange} language={language} />
      {/* Silent until it starts to matter. A permanent countdown makes people
          ration what they ask at exactly the wrong moment. */}
      {allowance && allowance.balance <= QUIET_ABOVE ? (
        <Text style={styles.left}>{t.messagesLeft(allowance.balance)}</Text>
      ) : null}
      <Button title={t.tarotRead} onPress={onRead} loading={loading} />
      <Text style={styles.note}>{t.tarotReadCost}</Text>
    </Card>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: {
    paddingHorizontal: space.lg,
    paddingBottom: space.xxl,
    gap: space.md,
  },
  kicker: { ...type.label, color: colors.textFaint, marginTop: space.sm },
  pressed: { opacity: 0.6 },

  ask: { gap: space.sm },
  input: {
    ...type.body,
    color: colors.text,
    backgroundColor: colors.surface,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.border,
    paddingHorizontal: space.md,
    paddingVertical: space.sm,
    minHeight: 64,
    textAlignVertical: 'top',
  },
  action: { marginTop: space.sm },

  spread: { flexDirection: 'row', gap: space.sm, marginTop: space.sm },
  column: { flex: 1, gap: space.sm },
  position: { ...type.label, fontSize: 9, color: colors.textFaint, textAlign: 'center' },
  hint: { ...type.body, fontSize: 13, color: colors.textFaint, textAlign: 'center' },

  detail: { gap: space.xs },
  detailHead: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    gap: space.sm,
  },
  detailPosition: { ...type.label, color: colors.textFaint },
  orient: {
    borderWidth: 1,
    borderRadius: radius.pill,
    paddingHorizontal: space.sm,
    paddingVertical: 2,
  },
  orientText: { fontSize: 9, fontWeight: '700', letterSpacing: 0.8 },
  cardName: { ...type.heading },
  keywords: { ...type.mono, color: colors.textFaint },
  meaning: { ...type.body, color: colors.text, lineHeight: 22, marginTop: space.xs },

  offer: { gap: space.sm, marginTop: space.sm },
  left: { ...type.mono, color: colors.textFaint, textAlign: 'center' },
  readingCard: { gap: space.md },
  flagged: { ...type.mono, color: colors.combust, lineHeight: 18 },

  gate: { gap: space.sm },
  gateTitle: { ...type.heading, color: colors.text },
  gateBody: { ...type.body, color: colors.textMuted, lineHeight: 22 },
  helplines: { ...type.body, color: colors.text, lineHeight: 22 },
  helplinesQuiet: { ...type.mono, color: colors.textFaint, lineHeight: 18 },

  seed: { ...type.mono, color: colors.textFaint, textAlign: 'center', marginTop: space.sm },
  note: { fontSize: 12, lineHeight: 18, color: colors.textFaint },

  deckLink: {
    marginTop: space.lg,
    paddingVertical: space.md,
    alignItems: 'center',
    borderTopWidth: StyleSheet.hairlineWidth,
    borderTopColor: colors.border,
  },
  deckLinkText: { ...type.label, color: colors.accentSoft },
});

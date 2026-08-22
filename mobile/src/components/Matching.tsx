/**
 * Ashtakoot Milan, inside the chart screen.
 *
 * **The shape of this screen is the argument.** The procedure scores two janma
 * nakshatras out of 36, and the harm it does is done by the total travelling
 * alone: a number below someone's threshold, handed down without the working.
 * So the total is never shown by itself — every koot sits under it with its own
 * points and the two values it was computed from, and the app's own line about
 * what the number is and is not sits under all of it.
 *
 * There is no verdict here, and there is not meant to be one. No colour for a
 * high score, no warning for a low one, no word like compatible. The backend
 * refuses to send one and this component would have nothing to draw with.
 *
 * The second person's birth details live only in this component's state. They
 * are not stored, not synced, and not sent anywhere but the one request that
 * computes the koots — someone else's birth time is not ours to keep.
 */

import { useCallback, useMemo, useState } from 'react';
import { ActivityIndicator, Pressable, StyleSheet, Text, TextInput, View } from 'react-native';

import { fetchMatch, searchPlaces } from '../api/client';
import type { BirthDetails, Match, Place } from '../api/types';
import { formatDateInput, formatTimeInput, toIsoDate, toIsoTime } from '../format';
import { strings, type DisplayLanguage } from '../i18n';
import { Button, Card, ErrorNote } from './ui';
import { colors, radius, space, type } from '../theme';

export function Matching({
  birth,
  language,
}: {
  birth: BirthDetails;
  language: DisplayLanguage;
}) {
  const t = strings(language);

  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [placeQuery, setPlaceQuery] = useState('');
  const [place, setPlace] = useState<Place | null>(null);
  const [results, setResults] = useState<Place[]>([]);
  const [searching, setSearching] = useState(false);

  const [match, setMatch] = useState<Match | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [running, setRunning] = useState(false);

  const isoDate = toIsoDate(date);
  const isoTime = toIsoTime(time);
  const ready = isoDate !== null && isoTime !== null && place !== null;

  const search = useCallback(async (query: string) => {
    setPlaceQuery(query);
    setPlace(null);
    if (query.trim().length < 2) {
      setResults([]);
      return;
    }
    setSearching(true);
    try {
      setResults(await searchPlaces(query, 6));
    } catch {
      setResults([]);
    } finally {
      setSearching(false);
    }
  }, []);

  const run = useCallback(async () => {
    if (!ready || !place || !isoDate || !isoTime) return;
    setRunning(true);
    setError(null);
    try {
      setMatch(
        await fetchMatch(birth, {
          date: isoDate,
          time: isoTime,
          latitude: place.latitude,
          longitude: place.longitude,
          place: `${place.name}, ${place.admin}`,
        }),
      );
    } catch (err) {
      setError(err instanceof Error ? err.message : t.unreachable);
    } finally {
      setRunning(false);
    }
  }, [ready, place, isoDate, isoTime, birth, t]);

  const total = useMemo(
    // Half points are real in this procedure — Tara and Vashya both produce
    // them — so the total is not always a whole number.
    () => (match ? String(match.total % 1 === 0 ? match.total : match.total.toFixed(1)) : ''),
    [match],
  );

  return (
    <View style={styles.wrap}>
      {/* No heading of its own: the screen's bar already says Milan, and the
          section title that used to sit here was written when this lived at the
          foot of the chart screen. */}
      <Text style={styles.intro}>{t.matchingIntro}</Text>

      {match ? (
        <>
          <Card>
            <View style={styles.totalRow}>
              <Text style={styles.total}>{t.matchScore(total, match.maximum)}</Text>
            </View>

            {/* The header the whole table hangs off: which nakshatra and rashi
                each side actually brought. Without it the eight rows below are
                someone else's arithmetic rather than yours. */}
            <View style={styles.parties}>
              <Text style={styles.party}>
                <Text style={styles.partyWho}>{t.matchYou}</Text>
                {'  '}
                {language === 'hi' ? match.bride_nakshatra_hi : match.bride_nakshatra}
                {' · '}
                {language === 'hi' ? match.bride_rashi_hi : match.bride_rashi}
              </Text>
              <Text style={styles.party}>
                <Text style={styles.partyWho}>{t.matchThem}</Text>
                {'  '}
                {language === 'hi' ? match.groom_nakshatra_hi : match.groom_nakshatra}
                {' · '}
                {language === 'hi' ? match.groom_rashi_hi : match.groom_rashi}
              </Text>
            </View>

            {match.koots.map((koot, index) => (
              <View key={koot.name} style={[styles.koot, index > 0 && styles.divided]}>
                <View style={styles.kootHead}>
                  <Text style={styles.kootName}>{t.koots[koot.name] ?? koot.name}</Text>
                  <Text style={styles.kootPoints}>
                    {koot.points % 1 === 0 ? koot.points : koot.points.toFixed(1)}
                    <Text style={styles.kootMax}> / {koot.maximum}</Text>
                  </Text>
                </View>
                <Text style={styles.kootWhy}>
                  {language === 'hi' ? koot.bride_hi : koot.bride}
                  {' · '}
                  {language === 'hi' ? koot.groom_hi : koot.groom}
                </Text>
              </View>
            ))}
          </Card>

          <Text style={styles.caption}>{t.matchCaption}</Text>

          <View style={styles.action}>
            <Button
              title={t.matchAgain}
              onPress={() => {
                setMatch(null);
                setError(null);
              }}
              variant="ghost"
            />
          </View>
        </>
      ) : (
        <>
          <Card>
            <Text style={styles.formLabel}>{t.matchPartnerLabel}</Text>

            <TextInput
              style={styles.input}
              value={date}
              onChangeText={(text) => setDate(formatDateInput(text, date))}
              placeholder="DD-MM-YYYY"
              placeholderTextColor={colors.textFaint}
              keyboardType="number-pad"
              maxLength={10}
            />
            <TextInput
              style={styles.input}
              value={time}
              onChangeText={(text) => setTime(formatTimeInput(text, time))}
              placeholder="HH:MM"
              placeholderTextColor={colors.textFaint}
              keyboardType="number-pad"
              maxLength={5}
            />

            <View>
              <TextInput
                style={styles.input}
                value={placeQuery}
                onChangeText={search}
                placeholder={t.matchPlaceSearch}
                placeholderTextColor={colors.textFaint}
                autoCorrect={false}
              />
              {searching ? (
                <ActivityIndicator style={styles.spinner} color={colors.textFaint} />
              ) : null}
            </View>

            {results.length > 0 && !place ? (
              <View style={styles.results}>
                {results.map((item) => (
                  <Pressable
                    key={`${item.name}-${item.latitude}-${item.longitude}`}
                    onPress={() => {
                      setPlace(item);
                      setPlaceQuery(`${item.name}, ${item.admin}`);
                      setResults([]);
                    }}
                    style={({ pressed }) => [styles.result, pressed && styles.pressed]}
                  >
                    <Text style={styles.resultName}>{item.name}</Text>
                    <Text style={styles.resultAdmin}>{item.admin}</Text>
                  </Pressable>
                ))}
              </View>
            ) : null}
          </Card>

          {error ? (
            <View style={styles.action}>
              <ErrorNote message={error} />
            </View>
          ) : null}

          <View style={styles.action}>
            <Button
              title={t.matchRun}
              onPress={run}
              disabled={!ready}
              loading={running}
            />
          </View>
        </>
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  wrap: { marginTop: space.lg },
  intro: { ...type.body, color: colors.textMuted, marginBottom: space.md, lineHeight: 22 },

  formLabel: { ...type.label, color: colors.textFaint, marginBottom: space.sm },
  input: {
    ...type.body,
    color: colors.text,
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.glassBorder,
    borderRadius: radius.md,
    paddingHorizontal: space.md,
    paddingVertical: space.sm + 2,
    marginBottom: space.sm,
  },
  spinner: { position: 'absolute', right: space.md, top: space.md },
  results: { gap: 2 },
  result: { paddingVertical: space.sm, paddingHorizontal: space.sm },
  pressed: { opacity: 0.6 },
  resultName: { ...type.body, color: colors.text },
  resultAdmin: { ...type.mono, color: colors.textFaint },

  // The total is large because it is what people look at — and it is placed
  // above the working rather than instead of it.
  totalRow: { alignItems: 'center', paddingVertical: space.sm },
  total: { ...type.display, color: colors.text },
  parties: {
    gap: space.xs,
    paddingBottom: space.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  party: { ...type.body, color: colors.textMuted },
  partyWho: { ...type.label, color: colors.accentSoft },

  koot: { paddingVertical: space.md },
  divided: { borderTopWidth: StyleSheet.hairlineWidth, borderTopColor: colors.border },
  kootHead: { flexDirection: 'row', justifyContent: 'space-between', alignItems: 'baseline' },
  kootName: { ...type.heading, color: colors.text },
  kootPoints: { ...type.heading, color: colors.text },
  kootMax: { ...type.body, color: colors.textFaint },
  kootWhy: { ...type.mono, color: colors.textMuted, marginTop: 2 },

  caption: { ...type.mono, color: colors.textFaint, marginTop: space.md, lineHeight: 18 },
  action: { marginTop: space.md },
});

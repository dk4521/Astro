/**
 * Birth details capture.
 *
 * Three facts decide every number the app will ever show: date, exact local
 * time, and place. The form is deliberately plain about that — precision here
 * is the whole product, and the lagna moves a full sign roughly every two
 * hours, so a vague time is worth saying out loud.
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

import { searchPlaces } from '../src/api/client';
import { saveBirthDetails } from '../src/api/storage';
import { useSync } from '../src/sync/context';
import type { Place } from '../src/api/types';
import { Button, ErrorNote, Label } from '../src/components/ui';
import {
  formatDateInput,
  formatTimeInput,
  toIsoDate,
  toIsoTime,
} from '../src/format';
import { colors, radius, space, type } from '../src/theme';

export default function Onboarding() {
  const router = useRouter();
  const insets = useSafeAreaInsets();
  const { pushBirth } = useSync();

  const [date, setDate] = useState('');
  const [time, setTime] = useState('');
  const [placeQuery, setPlaceQuery] = useState('');
  const [place, setPlace] = useState<Place | null>(null);
  const [results, setResults] = useState<Place[]>([]);
  const [searching, setSearching] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saving, setSaving] = useState(false);

  // Debounce so a fast typist does not fire a request per keystroke.
  const debounce = useRef<ReturnType<typeof setTimeout> | null>(null);
  const requestId = useRef(0);

  useEffect(() => {
    if (place && placeQuery === `${place.name}, ${place.admin}`) return;

    if (debounce.current) clearTimeout(debounce.current);

    const query = placeQuery.trim();
    if (query.length < 2) {
      setResults([]);
      setSearching(false);
      return;
    }

    setSearching(true);
    debounce.current = setTimeout(async () => {
      const id = ++requestId.current;
      try {
        const found = await searchPlaces(query);
        // Ignore a response that a newer keystroke has already superseded.
        if (id === requestId.current) {
          setResults(found);
          setError(null);
        }
      } catch (err) {
        if (id === requestId.current) {
          setResults([]);
          setError(err instanceof Error ? err.message : 'Place search failed');
        }
      } finally {
        if (id === requestId.current) setSearching(false);
      }
    }, 250);

    return () => {
      if (debounce.current) clearTimeout(debounce.current);
    };
  }, [placeQuery, place]);

  const selectPlace = useCallback((selected: Place) => {
    setPlace(selected);
    setPlaceQuery(`${selected.name}, ${selected.admin}`);
    setResults([]);
  }, []);

  // The field holds what the user sees; these are what the API gets.
  const isoDate = toIsoDate(date);
  const isoTime = toIsoTime(time);
  const dateValid = isoDate !== null;
  const timeValid = isoTime !== null;
  const ready = dateValid && timeValid && place !== null;

  const submit = useCallback(async () => {
    if (!ready || !place || !isoDate || !isoTime) return;
    setSaving(true);
    setError(null);
    try {
      const details = {
        date: isoDate,
        time: isoTime,
        latitude: place.latitude,
        longitude: place.longitude,
        place: `${place.name}, ${place.admin}`,
      };
      await saveBirthDetails(details);
      // Not awaited: the device already has the details, and the chart is what
      // this button promised. A failed upload is picked up by the next sync
      // rather than made into a reason to sit on a spinner.
      void pushBirth(details);
      router.replace('/chart');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Could not save your details');
      setSaving(false);
    }
  }, [ready, place, isoDate, isoTime, router, pushBirth]);

  return (
    // Android needs `padding` as much as iOS does here: with edge-to-edge the
    // window no longer resizes for the keyboard, and the place field — the last
    // one in the form — sat underneath it along with its search results.
    <KeyboardAvoidingView style={styles.flex} behavior="padding">
      <ScrollView
        contentContainerStyle={[
          styles.content,
          { paddingTop: insets.top + space.xl, paddingBottom: insets.bottom + space.xl },
        ]}
        keyboardShouldPersistTaps="handled"
      >
        <Text style={styles.kicker}>Kosmiq</Text>
        <Text style={styles.title}>Your birth chart{'\n'}starts with three facts.</Text>
        <View style={styles.field}>
          <Label>Date of birth</Label>
          <TextInput
            style={[styles.input, date.length > 0 && !dateValid && styles.inputError]}
            value={date}
            // Digits only: the dashes are placed for the typist rather than
            // asked of them, which is also why the keypad has no punctuation.
            onChangeText={(text) => setDate(formatDateInput(text, date))}
            placeholder="DD-MM-YYYY"
            placeholderTextColor={colors.textFaint}
            keyboardType="number-pad"
            autoCorrect={false}
            maxLength={10}
          />
          {date.length === 10 && !dateValid ? (
            <Text style={styles.hintError}>That date does not exist.</Text>
          ) : null}
        </View>

        <View style={styles.field}>
          <Label>Time of birth</Label>
          <TextInput
            style={[styles.input, time.length > 0 && !timeValid && styles.inputError]}
            value={time}
            onChangeText={(text) => setTime(formatTimeInput(text, time))}
            placeholder="HH:MM  (24-hour)"
            placeholderTextColor={colors.textFaint}
            keyboardType="number-pad"
            autoCorrect={false}
            maxLength={5}
          />
          {time.length === 5 && !timeValid ? (
            <Text style={styles.hintError}>Use a 24-hour clock, 00:00 to 23:59.</Text>
          ) : null}
        </View>

        <View style={styles.field}>
          <Label>Place of birth</Label>
          <View>
            <TextInput
              style={styles.input}
              value={placeQuery}
              onChangeText={(text) => {
                setPlaceQuery(text);
                setPlace(null);
              }}
              placeholder="Search a city"
              placeholderTextColor={colors.textFaint}
              autoCorrect={false}
            />
            {searching ? (
              <ActivityIndicator style={styles.inputSpinner} color={colors.textFaint} />
            ) : null}
          </View>

          {results.length > 0 ? (
            <View style={styles.results}>
              {results.map((item) => (
                <Pressable
                  key={`${item.name}-${item.latitude}-${item.longitude}`}
                  accessibilityRole="button"
                  onPress={() => selectPlace(item)}
                  style={({ pressed }) => [styles.result, pressed && styles.resultPressed]}
                >
                  <Text style={styles.resultName}>{item.name}</Text>
                  <Text style={styles.resultMeta}>
                    {item.admin} · {item.country}
                  </Text>
                </Pressable>
              ))}
            </View>
          ) : null}

          {place ? (
            <Text style={styles.hint}>
              {place.latitude.toFixed(4)}°, {place.longitude.toFixed(4)}°
            </Text>
          ) : null}
        </View>

        {error ? (
          <View style={styles.errorSlot}>
            <ErrorNote message={error} />
          </View>
        ) : null}

        <View style={styles.actions}>
          <Button
            title="Cast my chart"
            onPress={submit}
            disabled={!ready}
            loading={saving}
          />
        </View>
      </ScrollView>
    </KeyboardAvoidingView>
  );
}

const styles = StyleSheet.create({
  flex: { flex: 1, backgroundColor: 'transparent' },
  content: { paddingHorizontal: space.lg, gap: space.sm },
  kicker: { ...type.label, color: colors.accent, marginBottom: space.md },
  title: { ...type.display, color: colors.text, marginBottom: space.sm },
  subtitle: {
    ...type.body,
    color: colors.textMuted,
    lineHeight: 22,
    marginBottom: space.xl,
  },
  field: { marginBottom: space.lg },
  input: {
    backgroundColor: colors.glass,
    borderWidth: 1,
    borderColor: colors.border,
    borderRadius: radius.sm,
    paddingHorizontal: space.md,
    paddingVertical: space.md,
    color: colors.text,
    fontSize: 16,
  },
  inputError: { borderColor: colors.combust },
  inputSpinner: { position: 'absolute', right: space.md, top: 0, bottom: 0 },
  hint: { ...type.mono, color: colors.textFaint, marginTop: space.sm, lineHeight: 18 },
  hintError: { ...type.mono, color: colors.combust, marginTop: space.sm },
  results: {
    marginTop: space.sm,
    backgroundColor: colors.glassRaised,
    borderRadius: radius.sm,
    borderWidth: 1,
    borderColor: colors.border,
    overflow: 'hidden',
  },
  result: {
    paddingHorizontal: space.md,
    paddingVertical: space.md,
    borderBottomWidth: StyleSheet.hairlineWidth,
    borderBottomColor: colors.border,
  },
  resultPressed: { backgroundColor: colors.accentDim },
  resultName: { ...type.body, color: colors.text, fontWeight: '600' },
  resultMeta: { ...type.mono, color: colors.textFaint, marginTop: 2 },
  errorSlot: { marginBottom: space.md },
  actions: { marginTop: space.md },
});

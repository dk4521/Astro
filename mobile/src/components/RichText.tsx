/**
 * The model's output, rendered.
 *
 * Two problems, both only visible once real generated text reaches a screen:
 *
 * 1. **It is markdown.** The prompt contract asks for prose, and readings still
 *    come back with `**bold**` and `*` bullets. React Native's `Text` shows
 *    those as literal asterisks, so a reading looks broken. This is a
 *    deliberately tiny subset — bold, bullets, paragraphs — rather than a
 *    markdown dependency, because that is the whole of what arrives.
 *
 * 2. **Some of it is a phone number someone needs right now.** The crisis path
 *    answers with real helplines, and a number that has to be memorised and
 *    retyped is a number that does not get dialled. Only the numbers the
 *    contract itself names are linked — see `HELPLINES`, and keep it in step
 *    with `backend/app/ai/prompts.py`.
 */

import { Fragment, ReactNode, useMemo } from 'react';
import { Linking, StyleSheet, Text, TextStyle, View } from 'react-native';

import { colors, space, type } from '../theme';

/**
 * Dialable numbers named in the prompt contract. Nothing else is linked: this
 * is a fixed list rather than phone-number detection so a degree or a year can
 * never become a tappable call.
 */
const HELPLINES: { pattern: RegExp; dial: string }[] = [
  { pattern: /\b(?:1800[-\s]?89[-\s]?)?14416\b/, dial: 'tel:14416' }, // Tele-MANAS
  { pattern: /\+?\s?91[-\s]?9820466726\b|\b9820466726\b/, dial: 'tel:+919820466726' }, // AASRA
  { pattern: /\b181\b/, dial: 'tel:181' }, // Women Helpline
  { pattern: /\b112\b/, dial: 'tel:112' }, // Emergency, India
];

const BOLD = /\*\*([^*]+)\*\*/;

const BULLET = /^\s*[-*•]\s+/;

type Block = { kind: 'paragraph' | 'bullet'; text: string };

function parseBlocks(text: string): Block[] {
  return text
    .split('\n')
    .map((line) => line.trim())
    .filter((line) => line.length > 0)
    .map((line) =>
      BULLET.test(line)
        ? { kind: 'bullet' as const, text: line.replace(BULLET, '') }
        : // A stray heading marker would otherwise render as a hash.
          { kind: 'paragraph' as const, text: line.replace(/^#{1,6}\s+/, '') },
    );
}

/** Split one line into plain text, bold runs, and dialable numbers. */
function renderInline(line: string): ReactNode {
  const parts: ReactNode[] = [];
  let rest = line;
  let key = 0;

  while (rest.length > 0) {
    const bold = BOLD.exec(rest);
    const phone = findHelpline(rest);

    // Whichever marker comes first wins; neither means the rest is plain.
    const next = [bold, phone].filter(Boolean).sort((a, b) => a!.index - b!.index)[0];
    if (!next) {
      parts.push(<Fragment key={key++}>{rest}</Fragment>);
      break;
    }

    if (next.index > 0) parts.push(<Fragment key={key++}>{rest.slice(0, next.index)}</Fragment>);

    if (next === bold) {
      parts.push(
        <Text key={key++} style={styles.bold}>
          {bold![1]}
        </Text>,
      );
      rest = rest.slice(bold!.index + bold![0].length);
    } else {
      const matched = phone!.text;
      parts.push(
        <Text
          key={key++}
          style={styles.link}
          accessibilityRole="link"
          onPress={() => {
            Linking.openURL(phone!.dial).catch(() => {
              // A device with no dialler — a tablet, a simulator — should not
              // crash the reading. The number is still on screen to read.
            });
          }}
        >
          {matched}
        </Text>,
      );
      rest = rest.slice(phone!.index + matched.length);
    }
  }

  return parts;
}

function findHelpline(line: string): { index: number; text: string; dial: string } | null {
  let best: { index: number; text: string; dial: string } | null = null;

  for (const { pattern, dial } of HELPLINES) {
    const match = pattern.exec(line);
    if (match && (best === null || match.index < best.index)) {
      best = { index: match.index, text: match[0], dial };
    }
  }

  return best;
}

export function RichText({ text, style }: { text: string; style?: TextStyle }) {
  const blocks = useMemo(() => parseBlocks(text), [text]);

  return (
    <View style={styles.stack}>
      {blocks.map((block, index) =>
        block.kind === 'bullet' ? (
          <View key={index} style={styles.bulletRow}>
            <Text style={[styles.body, style, styles.bulletDot]}>•</Text>
            <Text style={[styles.body, style, styles.bulletText]}>
              {renderInline(block.text)}
            </Text>
          </View>
        ) : (
          <Text key={index} style={[styles.body, style]}>
            {renderInline(block.text)}
          </Text>
        ),
      )}
    </View>
  );
}

const styles = StyleSheet.create({
  stack: { gap: space.md },
  body: { ...type.body, color: colors.text, lineHeight: 24 },
  bold: { fontWeight: '700' },
  link: { color: colors.accentSoft, fontWeight: '700', textDecorationLine: 'underline' },
  bulletRow: { flexDirection: 'row', gap: space.sm, paddingRight: space.sm },
  bulletDot: { color: colors.textFaint },
  bulletText: { flex: 1 },
});

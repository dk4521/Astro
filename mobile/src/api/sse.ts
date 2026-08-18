/**
 * Server-sent event framing.
 *
 * Split out from `client.ts` for one reason: it is the only logic in the app
 * that cannot be judged by reading it. A stream arrives in chunks that fall
 * wherever the network put them — mid-event, mid-word, mid-UTF-8-sequence — so
 * the interesting cases are the ones a hand-run never produces. Here it is a
 * plain function of strings, with no `expo/fetch` and no React, so it can be
 * compiled and run against real captured bytes.
 *
 * Deliberately a subset of the SSE spec: the backend emits `event:` and `data:`
 * and nothing else, so `id:`, `retry:` and comment lines are ignored rather
 * than modelled.
 */

export type SseEvent = { name: string; data: string };

export class SseParser {
  private buffer = '';

  /**
   * Feed one decoded chunk; get back every event it completed.
   *
   * A trailing partial event stays in the buffer until the chunk that finishes
   * it, so a token split across two reads is delivered once, whole, and in
   * order — never twice and never truncated.
   */
  push(chunk: string): SseEvent[] {
    // Normalise CRLF so a proxy that rewrites line endings cannot hide the
    // blank line that terminates an event.
    this.buffer += chunk.replace(/\r\n/g, '\n');

    const events: SseEvent[] = [];
    let boundary = this.buffer.indexOf('\n\n');

    while (boundary !== -1) {
      const frame = this.buffer.slice(0, boundary);
      this.buffer = this.buffer.slice(boundary + 2);

      const event = parseFrame(frame);
      if (event) events.push(event);

      boundary = this.buffer.indexOf('\n\n');
    }

    return events;
  }
}

function parseFrame(frame: string): SseEvent | null {
  let name = 'message';
  const data: string[] = [];

  for (const line of frame.split('\n')) {
    if (line.startsWith('event:')) {
      name = line.slice(6).trim();
    } else if (line.startsWith('data:')) {
      // Exactly one leading space is part of the framing, not the payload; any
      // further whitespace belongs to the data.
      const value = line.slice(5);
      data.push(value.startsWith(' ') ? value.slice(1) : value);
    }
  }

  if (data.length === 0) return null;

  // Multi-line data is rejoined with newlines, as the spec requires.
  return { name, data: data.join('\n') };
}

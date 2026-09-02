/**
 * Backend client.
 *
 * The base URL is resolved rather than hard-coded: a phone running Expo Go
 * cannot reach the laptop's `localhost`, so in development we fall back to the
 * host that served the JS bundle, which is the laptop's LAN address.
 *
 * In a release build there is exactly one way to set it — `EXPO_PUBLIC_API_URL`,
 * supplied by the build profile in `eas.json`. There used to be a second, an
 * `extra.apiBaseUrl` in `app.json`, and two settings that can disagree is worse
 * than one: the `app.json` copy said `http://localhost:8000`, which in a store
 * build points the phone at itself. That failure is silent in the worst way —
 * the app installs, opens, and then every screen that needs the server fails
 * with an ordinary network error that says nothing about why.
 *
 * `API_NOT_CONFIGURED` below is the fix for that: it does not stop the build,
 * because a wrong URL is a deployment mistake rather than a reason to refuse to
 * launch, but the settings screen names it instead of leaving someone reading
 * timeouts.
 */

import Constants from 'expo-constants';
// Named import rather than the global: `expo/fetch` is the only fetch here that
// streams a response body, and importing it explicitly keeps working even if a
// build sets EXPO_PUBLIC_USE_RN_FETCH=1 and puts React Native's fetch back.
import { fetch as streamingFetch } from 'expo/fetch';

import { supabase } from '../auth/client';
import { SseParser, type SseEvent } from './sse';
import type {
  BirthDetails,
  ChatTurn,
  CourseChapter,
  CourseIndex,
  CourseLanguage,
  Interpretation,
  Language,
  Match,
  Place,
  Reading,
  TarotDeck,
  TarotDraw,
  TarotReading,
  Tip,
  Today,
} from './types';

const DEFAULT_PORT = 8000;

/** An address that only ever resolves on the machine asking for it. */
const LOOPBACK = /^https?:\/\/(localhost|127\.0\.0\.1|0\.0\.0\.0|\[::1\])(:|\/|$)/i;

function resolveBaseUrl(): string {
  const configured = process.env.EXPO_PUBLIC_API_URL?.trim();
  if (configured) return configured.replace(/\/$/, '');

  // In dev, rewrite the localhost default to the packager's host so a physical
  // device on the same network reaches the laptop instead of itself.
  const hostUri = Constants.expoConfig?.hostUri;
  if (__DEV__ && hostUri) {
    const host = hostUri.split(':')[0];
    if (host) return `http://${host}:${DEFAULT_PORT}`;
  }

  return `http://localhost:${DEFAULT_PORT}`;
}

export const API_BASE_URL = resolveBaseUrl();

/**
 * True when a release build was made without `EXPO_PUBLIC_API_URL`.
 *
 * There is no legitimate way for a shipped app to be pointing at a loopback
 * address: it is the phone talking to itself, and nothing served from the
 * backend — a chart, a reading, the course, place search — can answer.
 */
export const API_NOT_CONFIGURED = !__DEV__ && LOOPBACK.test(API_BASE_URL);

/**
 * The Supabase session, as a header the backend can verify.
 *
 * Read from the client rather than passed down from React, so there is no way
 * for a screen to send a token that went stale while it was mounted:
 * `getSession()` returns the refreshed one, and supabase-js has already done
 * the refreshing.
 *
 * Absent is a valid answer. The deterministic endpoints answer anyway, and the
 * ones behind Pro reply 401 — which is the app's cue to ask someone to sign in,
 * not a reason to have withheld the request. A signed-in reader without a
 * subscription gets 402 instead, which opens the plans screen.
 */
async function authHeader(): Promise<Record<string, string>> {
  if (!supabase) return {};
  try {
    const { data } = await supabase.auth.getSession();
    const token = data.session?.access_token;
    return token ? { Authorization: `Bearer ${token}` } : {};
  } catch {
    return {};
  }
}

export class ApiError extends Error {
  constructor(
    message: string,
    readonly status?: number,
  ) {
    super(message);
    this.name = 'ApiError';
  }
}

const TIMEOUT_MS = 15_000;

// Interpretation is a different kind of wait. The deterministic endpoints answer
// in milliseconds; a generated reading was measured between 2s and 80s on the
// free tier, because a busy model sends the request down the fallback chain
// before anyone answers. Fifteen seconds would abort most of them.
const INTERPRET_TIMEOUT_MS = 90_000;

async function request<T>(
  path: string,
  init?: RequestInit,
  timeoutMs: number = TIMEOUT_MS,
): Promise<T> {
  const controller = new AbortController();
  const timer = setTimeout(() => controller.abort(), timeoutMs);

  const auth = await authHeader();

  let response: Response;
  try {
    response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      signal: controller.signal,
      headers: { 'Content-Type': 'application/json', ...auth, ...init?.headers },
    });
  } catch (error) {
    // A failed fetch here is almost always the backend not running or the
    // device being unable to see it, so say that rather than "Network request
    // failed".
    const reason =
      error instanceof Error && error.name === 'AbortError'
        ? 'Request timed out'
        : 'Could not reach the server';
    throw new ApiError(`${reason} (${API_BASE_URL})`);
  } finally {
    clearTimeout(timer);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const body = await response.json();
      if (typeof body?.detail === 'string') detail = body.detail;
    } catch {
      // Response body was not JSON; the status-based message stands.
    }
    throw new ApiError(detail, response.status);
  }

  return (await response.json()) as T;
}

export function fetchReading(details: BirthDetails, levels = 2): Promise<Reading> {
  return request<Reading>(`/v1/reading?levels=${levels}`, {
    method: 'POST',
    body: JSON.stringify(details),
  });
}

/** Ashtakoot Milan. Deterministic, so no long timeout and no quota. */
export function fetchMatch(bride: BirthDetails, groom: BirthDetails): Promise<Match> {
  return request<Match>('/v1/match', {
    method: 'POST',
    body: JSON.stringify({ bride, groom }),
  });
}

export function searchPlaces(query: string, limit = 8): Promise<Place[]> {
  const params = new URLSearchParams({ q: query, limit: String(limit) });
  return request<Place[]>(`/v1/places?${params.toString()}`);
}

export function fetchToday(birth: BirthDetails): Promise<Today> {
  return request<Today>('/v1/today', {
    method: 'POST',
    body: JSON.stringify(birth),
  });
}

// --- Course -----------------------------------------------------------------
//
// The course is downloaded, not bundled: thirty chapters in two languages would
// weigh on every install for material read a chapter at a time, and a
// correction to teaching text should not need an app release.

export function fetchCourseIndex(language: CourseLanguage): Promise<CourseIndex> {
  return request<CourseIndex>(`/v1/course?language=${language}`);
}

export function fetchChapter(
  slug: string,
  language: CourseLanguage,
  birth: BirthDetails | null,
): Promise<CourseChapter> {
  return request<CourseChapter>(`/v1/course/${slug}?language=${language}`, {
    method: 'POST',
    body: JSON.stringify({ birth }),
  });
}

// --- Interpretation ---------------------------------------------------------

export function fetchInterpretation(
  birth: BirthDetails,
  language: Language,
): Promise<Interpretation> {
  return request<Interpretation>(
    '/v1/interpret',
    { method: 'POST', body: JSON.stringify({ birth, language }) },
    INTERPRET_TIMEOUT_MS,
  );
}

/**
 * The daily line. Goes through the same long timeout as a reading — it is a
 * model call, and a busy free tier walks the fallback chain before answering.
 */
export function fetchTip(
  birth: BirthDetails,
  language: Language,
  companion: string | null,
): Promise<Tip> {
  return request<Tip>(
    '/v1/tip',
    { method: 'POST', body: JSON.stringify({ birth, language, companion }) },
    INTERPRET_TIMEOUT_MS,
  );
}

export type ChatVerdict = {
  grounded: boolean;
  contradictions: string[];
};

export type ChatHandlers = {
  /** One streamed fragment. Called many times, in order. */
  onToken: (chunk: string) => void;
  /**
   * The grounding result, which arrives only after the last token. Grounding
   * cannot gate a stream — the reader has seen the text before there is a
   * complete claim to check — so the app shows the verdict after the fact.
   */
  onVerdict: (verdict: ChatVerdict) => void;
};

/**
 * Ask a question about a chart, streaming the answer.
 *
 * `history` carries the conversation so far and must begin with a user turn:
 * the backend folds the chart brief into `history[0]` whatever its role, so
 * handing it an assistant turn would send that text back as if the user had
 * written it. The opening reading therefore stays out of the history — the
 * model is re-sent the whole chart on every request regardless, so what it
 * loses is only its own phrasing, never a fact.
 *
 * Resolves when the stream ends. Aborting via `signal` resolves quietly, since
 * a user pressing stop is not an error.
 */
export async function streamChat(
  body: {
    birth: BirthDetails;
    question: string;
    language: Language;
    history: ChatTurn[];
  },
  handlers: ChatHandlers,
  signal?: AbortSignal,
): Promise<void> {
  const auth = await authHeader();

  let response;
  try {
    response = await streamingFetch(`${API_BASE_URL}/v1/chat`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
        Accept: 'text/event-stream',
        ...auth,
      },
      body: JSON.stringify({
        birth: body.birth,
        question: body.question,
        language: body.language,
        history: body.history,
      }),
      signal,
    });
  } catch (error) {
    if (isAbort(error)) return;
    throw new ApiError(`Could not reach the server (${API_BASE_URL})`);
  }

  if (!response.ok) {
    let detail = `Request failed (${response.status})`;
    try {
      const parsed = await response.json();
      if (typeof parsed?.detail === 'string') detail = parsed.detail;
    } catch {
      // Not JSON; the status-based message stands.
    }
    throw new ApiError(detail, response.status);
  }

  if (!response.body) throw new ApiError('The server sent no stream');

  const reader = response.body.getReader();
  const decoder = new TextDecoder();
  const parser = new SseParser();

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;

      // A chunk can split a multi-byte character as easily as an event, so
      // decode in streaming mode and let the parser hold any partial frame.
      for (const event of parser.push(decoder.decode(value, { stream: true }))) {
        dispatch(event, handlers);
      }
    }
  } catch (error) {
    if (!isAbort(error)) throw error;
  } finally {
    reader.cancel().catch(() => {});
  }
}

function isAbort(error: unknown): boolean {
  return error instanceof Error && error.name === 'AbortError';
}

/** Turn one parsed event into a call on the handlers. */
function dispatch(event: SseEvent, handlers: ChatHandlers): void {
  const { name } = event;

  let payload: { text?: string; detail?: string } & Partial<ChatVerdict>;
  try {
    payload = JSON.parse(event.data);
  } catch {
    return; // A frame we cannot read is not worth failing the whole answer for.
  }

  if (name === 'token' && typeof payload.text === 'string') {
    handlers.onToken(payload.text);
  } else if (name === 'done') {
    handlers.onVerdict({
      grounded: payload.grounded ?? true,
      contradictions: payload.contradictions ?? [],
    });
  } else if (name === 'error') {
    // The stream can fail after text has already reached the reader — capacity
    // dropping mid-answer is the usual cause — so this is thrown rather than
    // returned, and the screen keeps whatever was said before it.
    throw new ApiError(payload.detail ?? 'The reading was interrupted');
  }
}

// --- Tarot ------------------------------------------------------------------
//
// The draw costs nothing and calls no model: the cards come from a seeded
// shuffle and every line that arrives with them was written by a person. Only
// the reading below spends anything.

export function fetchTarotDeck(): Promise<TarotDeck> {
  return request<TarotDeck>('/v1/tarot/deck');
}

/** Deal three cards. Pass a previous `seed` to deal that exact hand again. */
export function drawTarot(seed?: string): Promise<TarotDraw> {
  return request<TarotDraw>('/v1/tarot/draw', {
    method: 'POST',
    body: JSON.stringify({ seed: seed ?? null }),
  });
}

/**
 * Read a spread. Needs Pro, and goes through the long timeout for the same
 * reason a chart reading does — a busy free tier walks its fallback chain
 * before anyone answers.
 *
 * The cards are not sent. The server deals them again from the seed, so a
 * modified app cannot assemble a flattering spread and ask for words about it.
 */
export function fetchTarotReading(body: {
  seed: string;
  question: string | null;
  language: Language;
}): Promise<TarotReading> {
  return request<TarotReading>(
    '/v1/tarot/reading',
    {
      method: 'POST',
      body: JSON.stringify({
        seed: body.seed,
        question: body.question,
        language: body.language,
      }),
    },
    INTERPRET_TIMEOUT_MS,
  );
}
